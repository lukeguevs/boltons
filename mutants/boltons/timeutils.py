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

"""Python's :mod:`datetime` module provides some of the most complex
and powerful primitives in the Python standard library. Time is
nontrivial, but thankfully its support is first-class in
Python. ``dateutils`` provides some additional tools for working with
time.

Additionally, timeutils provides a few basic utilities for working
with timezones in Python. The Python :mod:`datetime` module's
documentation describes how to create a
:class:`~datetime.datetime`-compatible :class:`~datetime.tzinfo`
subtype. It even provides a few examples.

The following module defines usable forms of the timezones in those
docs, as well as a couple other useful ones, :data:`UTC` (aka GMT) and
:data:`LocalTZ` (representing the local timezone as configured in the
operating system). For timezones beyond these, as well as a higher
degree of accuracy in corner cases, check out `pytz`_ and `dateutil`_.

.. _pytz: https://pypi.python.org/pypi/pytz
.. _dateutil: https://dateutil.readthedocs.io/en/stable/index.html
"""

import re
import time
import bisect
import operator
from datetime import tzinfo, timedelta, date, datetime, timezone


# For legacy compatibility.
# boltons used to offer an implementation of total_seconds for Python <2.7
total_seconds = timedelta.total_seconds
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


def x_dt_to_timestamp__mutmut_orig(dt):
    """Converts from a :class:`~datetime.datetime` object to an integer
    timestamp, suitable interoperation with :func:`time.time` and
    other `Epoch-based timestamps`.

    .. _Epoch-based timestamps: https://en.wikipedia.org/wiki/Unix_time

    >>> timestamp = int(time.time())
    >>> utc_dt = datetime.fromtimestamp(timestamp, timezone.utc)
    >>> timestamp - dt_to_timestamp(utc_dt)
    0.0

    ``dt_to_timestamp`` supports both timezone-aware and naïve
    :class:`~datetime.datetime` objects. Note that it assumes naïve
    datetime objects are implied UTC, such as those generated with
    :meth:`datetime.datetime.utcnow`. If your datetime objects are
    local time, such as those generated with
    :meth:`datetime.datetime.now`, first convert it using the
    :meth:`datetime.datetime.replace` method with ``tzinfo=``
    :class:`LocalTZ` object in this module, then pass the result of
    that to ``dt_to_timestamp``.
    """
    if dt.tzinfo:
        td = dt - EPOCH_AWARE
    else:
        td = dt.replace(tzinfo=timezone.utc) - EPOCH_AWARE
    return timedelta.total_seconds(td)


def x_dt_to_timestamp__mutmut_1(dt):
    """Converts from a :class:`~datetime.datetime` object to an integer
    timestamp, suitable interoperation with :func:`time.time` and
    other `Epoch-based timestamps`.

    .. _Epoch-based timestamps: https://en.wikipedia.org/wiki/Unix_time

    >>> timestamp = int(time.time())
    >>> utc_dt = datetime.fromtimestamp(timestamp, timezone.utc)
    >>> timestamp - dt_to_timestamp(utc_dt)
    0.0

    ``dt_to_timestamp`` supports both timezone-aware and naïve
    :class:`~datetime.datetime` objects. Note that it assumes naïve
    datetime objects are implied UTC, such as those generated with
    :meth:`datetime.datetime.utcnow`. If your datetime objects are
    local time, such as those generated with
    :meth:`datetime.datetime.now`, first convert it using the
    :meth:`datetime.datetime.replace` method with ``tzinfo=``
    :class:`LocalTZ` object in this module, then pass the result of
    that to ``dt_to_timestamp``.
    """
    if dt.tzinfo:
        td = None
    else:
        td = dt.replace(tzinfo=timezone.utc) - EPOCH_AWARE
    return timedelta.total_seconds(td)


def x_dt_to_timestamp__mutmut_2(dt):
    """Converts from a :class:`~datetime.datetime` object to an integer
    timestamp, suitable interoperation with :func:`time.time` and
    other `Epoch-based timestamps`.

    .. _Epoch-based timestamps: https://en.wikipedia.org/wiki/Unix_time

    >>> timestamp = int(time.time())
    >>> utc_dt = datetime.fromtimestamp(timestamp, timezone.utc)
    >>> timestamp - dt_to_timestamp(utc_dt)
    0.0

    ``dt_to_timestamp`` supports both timezone-aware and naïve
    :class:`~datetime.datetime` objects. Note that it assumes naïve
    datetime objects are implied UTC, such as those generated with
    :meth:`datetime.datetime.utcnow`. If your datetime objects are
    local time, such as those generated with
    :meth:`datetime.datetime.now`, first convert it using the
    :meth:`datetime.datetime.replace` method with ``tzinfo=``
    :class:`LocalTZ` object in this module, then pass the result of
    that to ``dt_to_timestamp``.
    """
    if dt.tzinfo:
        td = dt + EPOCH_AWARE
    else:
        td = dt.replace(tzinfo=timezone.utc) - EPOCH_AWARE
    return timedelta.total_seconds(td)


def x_dt_to_timestamp__mutmut_3(dt):
    """Converts from a :class:`~datetime.datetime` object to an integer
    timestamp, suitable interoperation with :func:`time.time` and
    other `Epoch-based timestamps`.

    .. _Epoch-based timestamps: https://en.wikipedia.org/wiki/Unix_time

    >>> timestamp = int(time.time())
    >>> utc_dt = datetime.fromtimestamp(timestamp, timezone.utc)
    >>> timestamp - dt_to_timestamp(utc_dt)
    0.0

    ``dt_to_timestamp`` supports both timezone-aware and naïve
    :class:`~datetime.datetime` objects. Note that it assumes naïve
    datetime objects are implied UTC, such as those generated with
    :meth:`datetime.datetime.utcnow`. If your datetime objects are
    local time, such as those generated with
    :meth:`datetime.datetime.now`, first convert it using the
    :meth:`datetime.datetime.replace` method with ``tzinfo=``
    :class:`LocalTZ` object in this module, then pass the result of
    that to ``dt_to_timestamp``.
    """
    if dt.tzinfo:
        td = dt - EPOCH_AWARE
    else:
        td = None
    return timedelta.total_seconds(td)


def x_dt_to_timestamp__mutmut_4(dt):
    """Converts from a :class:`~datetime.datetime` object to an integer
    timestamp, suitable interoperation with :func:`time.time` and
    other `Epoch-based timestamps`.

    .. _Epoch-based timestamps: https://en.wikipedia.org/wiki/Unix_time

    >>> timestamp = int(time.time())
    >>> utc_dt = datetime.fromtimestamp(timestamp, timezone.utc)
    >>> timestamp - dt_to_timestamp(utc_dt)
    0.0

    ``dt_to_timestamp`` supports both timezone-aware and naïve
    :class:`~datetime.datetime` objects. Note that it assumes naïve
    datetime objects are implied UTC, such as those generated with
    :meth:`datetime.datetime.utcnow`. If your datetime objects are
    local time, such as those generated with
    :meth:`datetime.datetime.now`, first convert it using the
    :meth:`datetime.datetime.replace` method with ``tzinfo=``
    :class:`LocalTZ` object in this module, then pass the result of
    that to ``dt_to_timestamp``.
    """
    if dt.tzinfo:
        td = dt - EPOCH_AWARE
    else:
        td = dt.replace(tzinfo=timezone.utc) + EPOCH_AWARE
    return timedelta.total_seconds(td)


def x_dt_to_timestamp__mutmut_5(dt):
    """Converts from a :class:`~datetime.datetime` object to an integer
    timestamp, suitable interoperation with :func:`time.time` and
    other `Epoch-based timestamps`.

    .. _Epoch-based timestamps: https://en.wikipedia.org/wiki/Unix_time

    >>> timestamp = int(time.time())
    >>> utc_dt = datetime.fromtimestamp(timestamp, timezone.utc)
    >>> timestamp - dt_to_timestamp(utc_dt)
    0.0

    ``dt_to_timestamp`` supports both timezone-aware and naïve
    :class:`~datetime.datetime` objects. Note that it assumes naïve
    datetime objects are implied UTC, such as those generated with
    :meth:`datetime.datetime.utcnow`. If your datetime objects are
    local time, such as those generated with
    :meth:`datetime.datetime.now`, first convert it using the
    :meth:`datetime.datetime.replace` method with ``tzinfo=``
    :class:`LocalTZ` object in this module, then pass the result of
    that to ``dt_to_timestamp``.
    """
    if dt.tzinfo:
        td = dt - EPOCH_AWARE
    else:
        td = dt.replace(tzinfo=None) - EPOCH_AWARE
    return timedelta.total_seconds(td)


def x_dt_to_timestamp__mutmut_6(dt):
    """Converts from a :class:`~datetime.datetime` object to an integer
    timestamp, suitable interoperation with :func:`time.time` and
    other `Epoch-based timestamps`.

    .. _Epoch-based timestamps: https://en.wikipedia.org/wiki/Unix_time

    >>> timestamp = int(time.time())
    >>> utc_dt = datetime.fromtimestamp(timestamp, timezone.utc)
    >>> timestamp - dt_to_timestamp(utc_dt)
    0.0

    ``dt_to_timestamp`` supports both timezone-aware and naïve
    :class:`~datetime.datetime` objects. Note that it assumes naïve
    datetime objects are implied UTC, such as those generated with
    :meth:`datetime.datetime.utcnow`. If your datetime objects are
    local time, such as those generated with
    :meth:`datetime.datetime.now`, first convert it using the
    :meth:`datetime.datetime.replace` method with ``tzinfo=``
    :class:`LocalTZ` object in this module, then pass the result of
    that to ``dt_to_timestamp``.
    """
    if dt.tzinfo:
        td = dt - EPOCH_AWARE
    else:
        td = dt.replace(tzinfo=timezone.utc) - EPOCH_AWARE
    return timedelta.total_seconds(None)

x_dt_to_timestamp__mutmut_mutants : ClassVar[MutantDict] = {
'x_dt_to_timestamp__mutmut_1': x_dt_to_timestamp__mutmut_1, 
    'x_dt_to_timestamp__mutmut_2': x_dt_to_timestamp__mutmut_2, 
    'x_dt_to_timestamp__mutmut_3': x_dt_to_timestamp__mutmut_3, 
    'x_dt_to_timestamp__mutmut_4': x_dt_to_timestamp__mutmut_4, 
    'x_dt_to_timestamp__mutmut_5': x_dt_to_timestamp__mutmut_5, 
    'x_dt_to_timestamp__mutmut_6': x_dt_to_timestamp__mutmut_6
}

def dt_to_timestamp(*args, **kwargs):
    result = _mutmut_trampoline(x_dt_to_timestamp__mutmut_orig, x_dt_to_timestamp__mutmut_mutants, args, kwargs)
    return result 

dt_to_timestamp.__signature__ = _mutmut_signature(x_dt_to_timestamp__mutmut_orig)
x_dt_to_timestamp__mutmut_orig.__name__ = 'x_dt_to_timestamp'


_NONDIGIT_RE = re.compile(r'\D')


def x_isoparse__mutmut_orig(iso_str):
    """Parses the limited subset of `ISO8601-formatted time`_ strings as
    returned by :meth:`datetime.datetime.isoformat`.

    >>> epoch_dt = datetime.fromtimestamp(0, timezone.utc).replace(tzinfo=None)
    >>> iso_str = epoch_dt.isoformat()
    >>> print(iso_str)
    1970-01-01T00:00:00
    >>> isoparse(iso_str)
    datetime.datetime(1970, 1, 1, 0, 0)

    >>> utcnow = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> utcnow == isoparse(utcnow.isoformat())
    True

    For further datetime parsing, see the `iso8601`_ package for strict
    ISO parsing and `dateutil`_ package for loose parsing and more.

    .. _ISO8601-formatted time: https://en.wikipedia.org/wiki/ISO_8601
    .. _iso8601: https://pypi.python.org/pypi/iso8601
    .. _dateutil: https://pypi.python.org/pypi/python-dateutil

    """
    dt_args = [int(p) for p in _NONDIGIT_RE.split(iso_str)]
    return datetime(*dt_args)


def x_isoparse__mutmut_1(iso_str):
    """Parses the limited subset of `ISO8601-formatted time`_ strings as
    returned by :meth:`datetime.datetime.isoformat`.

    >>> epoch_dt = datetime.fromtimestamp(0, timezone.utc).replace(tzinfo=None)
    >>> iso_str = epoch_dt.isoformat()
    >>> print(iso_str)
    1970-01-01T00:00:00
    >>> isoparse(iso_str)
    datetime.datetime(1970, 1, 1, 0, 0)

    >>> utcnow = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> utcnow == isoparse(utcnow.isoformat())
    True

    For further datetime parsing, see the `iso8601`_ package for strict
    ISO parsing and `dateutil`_ package for loose parsing and more.

    .. _ISO8601-formatted time: https://en.wikipedia.org/wiki/ISO_8601
    .. _iso8601: https://pypi.python.org/pypi/iso8601
    .. _dateutil: https://pypi.python.org/pypi/python-dateutil

    """
    dt_args = None
    return datetime(*dt_args)


def x_isoparse__mutmut_2(iso_str):
    """Parses the limited subset of `ISO8601-formatted time`_ strings as
    returned by :meth:`datetime.datetime.isoformat`.

    >>> epoch_dt = datetime.fromtimestamp(0, timezone.utc).replace(tzinfo=None)
    >>> iso_str = epoch_dt.isoformat()
    >>> print(iso_str)
    1970-01-01T00:00:00
    >>> isoparse(iso_str)
    datetime.datetime(1970, 1, 1, 0, 0)

    >>> utcnow = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> utcnow == isoparse(utcnow.isoformat())
    True

    For further datetime parsing, see the `iso8601`_ package for strict
    ISO parsing and `dateutil`_ package for loose parsing and more.

    .. _ISO8601-formatted time: https://en.wikipedia.org/wiki/ISO_8601
    .. _iso8601: https://pypi.python.org/pypi/iso8601
    .. _dateutil: https://pypi.python.org/pypi/python-dateutil

    """
    dt_args = [int(None) for p in _NONDIGIT_RE.split(iso_str)]
    return datetime(*dt_args)


def x_isoparse__mutmut_3(iso_str):
    """Parses the limited subset of `ISO8601-formatted time`_ strings as
    returned by :meth:`datetime.datetime.isoformat`.

    >>> epoch_dt = datetime.fromtimestamp(0, timezone.utc).replace(tzinfo=None)
    >>> iso_str = epoch_dt.isoformat()
    >>> print(iso_str)
    1970-01-01T00:00:00
    >>> isoparse(iso_str)
    datetime.datetime(1970, 1, 1, 0, 0)

    >>> utcnow = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> utcnow == isoparse(utcnow.isoformat())
    True

    For further datetime parsing, see the `iso8601`_ package for strict
    ISO parsing and `dateutil`_ package for loose parsing and more.

    .. _ISO8601-formatted time: https://en.wikipedia.org/wiki/ISO_8601
    .. _iso8601: https://pypi.python.org/pypi/iso8601
    .. _dateutil: https://pypi.python.org/pypi/python-dateutil

    """
    dt_args = [int(p) for p in _NONDIGIT_RE.split(None)]
    return datetime(*dt_args)

x_isoparse__mutmut_mutants : ClassVar[MutantDict] = {
'x_isoparse__mutmut_1': x_isoparse__mutmut_1, 
    'x_isoparse__mutmut_2': x_isoparse__mutmut_2, 
    'x_isoparse__mutmut_3': x_isoparse__mutmut_3
}

def isoparse(*args, **kwargs):
    result = _mutmut_trampoline(x_isoparse__mutmut_orig, x_isoparse__mutmut_mutants, args, kwargs)
    return result 

isoparse.__signature__ = _mutmut_signature(x_isoparse__mutmut_orig)
x_isoparse__mutmut_orig.__name__ = 'x_isoparse'


_BOUNDS = [(0, timedelta(seconds=1), 'second'),
           (1, timedelta(seconds=60), 'minute'),
           (1, timedelta(seconds=3600), 'hour'),
           (1, timedelta(days=1), 'day'),
           (1, timedelta(days=7), 'week'),
           (2, timedelta(days=30), 'month'),
           (1, timedelta(days=365), 'year')]
_BOUNDS = [(b[0] * b[1], b[1], b[2]) for b in _BOUNDS]
_BOUND_DELTAS = [b[0] for b in _BOUNDS]

_FLOAT_PATTERN = r'[+-]?\ *(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?'
_PARSE_TD_RE = re.compile(r"((?P<value>%s)\s*(?P<unit>\w)\w*)" % _FLOAT_PATTERN)
_PARSE_TD_KW_MAP = {unit[0]: unit + 's'
                         for _, _, unit in reversed(_BOUNDS[:-2])}


def x_parse_timedelta__mutmut_orig(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('value'), match.group('unit')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_1(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = None
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('value'), match.group('unit')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_2(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(None):
        value, unit = match.group('value'), match.group('unit')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_3(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = None
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_4(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group(None), match.group('unit')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_5(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('XXvalueXX'), match.group('unit')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_6(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('VALUE'), match.group('unit')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_7(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('value'), match.group(None)
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_8(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('value'), match.group('XXunitXX')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_9(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('value'), match.group('UNIT')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_10(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('value'), match.group('unit')
        try:
            unit_key = None
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_11(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('value'), match.group('unit')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError(None)
        try:
            value = float(value)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_12(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('value'), match.group('unit')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r' / (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_13(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('value'), match.group('unit')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('XXinvalid time unit %r, expected one of %rXX'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_14(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('value'), match.group('unit')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('INVALID TIME UNIT %R, EXPECTED ONE OF %R'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_15(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('value'), match.group('unit')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = None
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_16(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('value'), match.group('unit')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(None)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_17(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('value'), match.group('unit')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError(None)
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_18(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('value'), match.group('unit')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r' / (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_19(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('value'), match.group('unit')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('XXinvalid time value for unit %r: %rXX'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_20(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('value'), match.group('unit')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('INVALID TIME VALUE FOR UNIT %R: %R'
                             % (unit, value))
        td_kwargs[unit_key] = value
    return timedelta(**td_kwargs)


def x_parse_timedelta__mutmut_21(text):
    """Robustly parses a short text description of a time period into a
    :class:`datetime.timedelta`. Supports weeks, days, hours, minutes,
    and seconds, with or without decimal points:

    Args:
        text (str): Text to parse.
    Returns:
        datetime.timedelta
    Raises:
        ValueError: on parse failure.

    >>> parse_td('1d 2h 3.5m 0s') == timedelta(days=1, seconds=7410)
    True

    Also supports full words and whitespace.

    >>> parse_td('2 weeks 1 day') == timedelta(days=15)
    True

    Negative times are supported, too:

    >>> parse_td('-1.5 weeks 3m 20s') == timedelta(days=-11, seconds=43400)
    True
    """
    td_kwargs = {}
    for match in _PARSE_TD_RE.finditer(text):
        value, unit = match.group('value'), match.group('unit')
        try:
            unit_key = _PARSE_TD_KW_MAP[unit]
        except KeyError:
            raise ValueError('invalid time unit %r, expected one of %r'
                             % (unit, _PARSE_TD_KW_MAP.keys()))
        try:
            value = float(value)
        except ValueError:
            raise ValueError('invalid time value for unit %r: %r'
                             % (unit, value))
        td_kwargs[unit_key] = None
    return timedelta(**td_kwargs)

x_parse_timedelta__mutmut_mutants : ClassVar[MutantDict] = {
'x_parse_timedelta__mutmut_1': x_parse_timedelta__mutmut_1, 
    'x_parse_timedelta__mutmut_2': x_parse_timedelta__mutmut_2, 
    'x_parse_timedelta__mutmut_3': x_parse_timedelta__mutmut_3, 
    'x_parse_timedelta__mutmut_4': x_parse_timedelta__mutmut_4, 
    'x_parse_timedelta__mutmut_5': x_parse_timedelta__mutmut_5, 
    'x_parse_timedelta__mutmut_6': x_parse_timedelta__mutmut_6, 
    'x_parse_timedelta__mutmut_7': x_parse_timedelta__mutmut_7, 
    'x_parse_timedelta__mutmut_8': x_parse_timedelta__mutmut_8, 
    'x_parse_timedelta__mutmut_9': x_parse_timedelta__mutmut_9, 
    'x_parse_timedelta__mutmut_10': x_parse_timedelta__mutmut_10, 
    'x_parse_timedelta__mutmut_11': x_parse_timedelta__mutmut_11, 
    'x_parse_timedelta__mutmut_12': x_parse_timedelta__mutmut_12, 
    'x_parse_timedelta__mutmut_13': x_parse_timedelta__mutmut_13, 
    'x_parse_timedelta__mutmut_14': x_parse_timedelta__mutmut_14, 
    'x_parse_timedelta__mutmut_15': x_parse_timedelta__mutmut_15, 
    'x_parse_timedelta__mutmut_16': x_parse_timedelta__mutmut_16, 
    'x_parse_timedelta__mutmut_17': x_parse_timedelta__mutmut_17, 
    'x_parse_timedelta__mutmut_18': x_parse_timedelta__mutmut_18, 
    'x_parse_timedelta__mutmut_19': x_parse_timedelta__mutmut_19, 
    'x_parse_timedelta__mutmut_20': x_parse_timedelta__mutmut_20, 
    'x_parse_timedelta__mutmut_21': x_parse_timedelta__mutmut_21
}

def parse_timedelta(*args, **kwargs):
    result = _mutmut_trampoline(x_parse_timedelta__mutmut_orig, x_parse_timedelta__mutmut_mutants, args, kwargs)
    return result 

parse_timedelta.__signature__ = _mutmut_signature(x_parse_timedelta__mutmut_orig)
x_parse_timedelta__mutmut_orig.__name__ = 'x_parse_timedelta'


parse_td = parse_timedelta  # legacy alias


def x__cardinalize_time_unit__mutmut_orig(unit, value):
    # removes dependency on strutils; nice and simple because
    # all time units cardinalize normally
    if value == 1:
        return unit
    return unit + 's'


def x__cardinalize_time_unit__mutmut_1(unit, value):
    # removes dependency on strutils; nice and simple because
    # all time units cardinalize normally
    if value != 1:
        return unit
    return unit + 's'


def x__cardinalize_time_unit__mutmut_2(unit, value):
    # removes dependency on strutils; nice and simple because
    # all time units cardinalize normally
    if value == 2:
        return unit
    return unit + 's'


def x__cardinalize_time_unit__mutmut_3(unit, value):
    # removes dependency on strutils; nice and simple because
    # all time units cardinalize normally
    if value == 1:
        return unit
    return unit - 's'


def x__cardinalize_time_unit__mutmut_4(unit, value):
    # removes dependency on strutils; nice and simple because
    # all time units cardinalize normally
    if value == 1:
        return unit
    return unit + 'XXsXX'


def x__cardinalize_time_unit__mutmut_5(unit, value):
    # removes dependency on strutils; nice and simple because
    # all time units cardinalize normally
    if value == 1:
        return unit
    return unit + 'S'

x__cardinalize_time_unit__mutmut_mutants : ClassVar[MutantDict] = {
'x__cardinalize_time_unit__mutmut_1': x__cardinalize_time_unit__mutmut_1, 
    'x__cardinalize_time_unit__mutmut_2': x__cardinalize_time_unit__mutmut_2, 
    'x__cardinalize_time_unit__mutmut_3': x__cardinalize_time_unit__mutmut_3, 
    'x__cardinalize_time_unit__mutmut_4': x__cardinalize_time_unit__mutmut_4, 
    'x__cardinalize_time_unit__mutmut_5': x__cardinalize_time_unit__mutmut_5
}

def _cardinalize_time_unit(*args, **kwargs):
    result = _mutmut_trampoline(x__cardinalize_time_unit__mutmut_orig, x__cardinalize_time_unit__mutmut_mutants, args, kwargs)
    return result 

_cardinalize_time_unit.__signature__ = _mutmut_signature(x__cardinalize_time_unit__mutmut_orig)
x__cardinalize_time_unit__mutmut_orig.__name__ = 'x__cardinalize_time_unit'


def x_decimal_relative_time__mutmut_orig(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_1(d, other=None, ndigits=1, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_2(d, other=None, ndigits=0, cardinalize=False):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_3(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is not None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_4(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = None
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_5(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(None).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_6(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = None
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_7(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other + d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_8(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = None
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_9(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(None)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_10(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = None
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_11(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(None)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_12(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = None
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_13(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) + 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_14(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(None, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_15(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, None) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_16(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_17(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, ) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_18(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 2
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_19(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = None
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_20(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = None
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_21(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds * timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_22(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(None)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_23(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = None
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_24(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(None, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_25(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, None)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_26(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_27(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, )
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_28(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(None, abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_29(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, None)
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_30(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(abs(rounded_diff))
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_31(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, )
    return rounded_diff, bname


def x_decimal_relative_time__mutmut_32(d, other=None, ndigits=0, cardinalize=True):
    """Get a tuple representing the relative time difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and now.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
        cardinalize (bool): Whether to pluralize the time unit if
            appropriate, defaults to ``True``.
    Returns:
        (float, str): A tuple of the :class:`float` difference and
           respective unit of time, pluralized if appropriate and
           *cardinalize* is set to ``True``.

    Unlike :func:`relative_time`, this method's return is amenable to
    localization into other languages and custom phrasing and
    formatting.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> decimal_relative_time(now - timedelta(days=1, seconds=3600), now)
    (1.0, 'day')
    >>> decimal_relative_time(now - timedelta(seconds=0.002), now, ndigits=5)
    (0.002, 'seconds')
    >>> decimal_relative_time(now, now - timedelta(days=900), ndigits=1)
    (-2.5, 'years')

    """
    if other is None:
        other = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = other - d
    diff_seconds = timedelta.total_seconds(diff)
    abs_diff = abs(diff)
    b_idx = bisect.bisect(_BOUND_DELTAS, abs_diff) - 1
    bbound, bunit, bname = _BOUNDS[b_idx]
    f_diff = diff_seconds / timedelta.total_seconds(bunit)
    rounded_diff = round(f_diff, ndigits)
    if cardinalize:
        return rounded_diff, _cardinalize_time_unit(bname, abs(None))
    return rounded_diff, bname

x_decimal_relative_time__mutmut_mutants : ClassVar[MutantDict] = {
'x_decimal_relative_time__mutmut_1': x_decimal_relative_time__mutmut_1, 
    'x_decimal_relative_time__mutmut_2': x_decimal_relative_time__mutmut_2, 
    'x_decimal_relative_time__mutmut_3': x_decimal_relative_time__mutmut_3, 
    'x_decimal_relative_time__mutmut_4': x_decimal_relative_time__mutmut_4, 
    'x_decimal_relative_time__mutmut_5': x_decimal_relative_time__mutmut_5, 
    'x_decimal_relative_time__mutmut_6': x_decimal_relative_time__mutmut_6, 
    'x_decimal_relative_time__mutmut_7': x_decimal_relative_time__mutmut_7, 
    'x_decimal_relative_time__mutmut_8': x_decimal_relative_time__mutmut_8, 
    'x_decimal_relative_time__mutmut_9': x_decimal_relative_time__mutmut_9, 
    'x_decimal_relative_time__mutmut_10': x_decimal_relative_time__mutmut_10, 
    'x_decimal_relative_time__mutmut_11': x_decimal_relative_time__mutmut_11, 
    'x_decimal_relative_time__mutmut_12': x_decimal_relative_time__mutmut_12, 
    'x_decimal_relative_time__mutmut_13': x_decimal_relative_time__mutmut_13, 
    'x_decimal_relative_time__mutmut_14': x_decimal_relative_time__mutmut_14, 
    'x_decimal_relative_time__mutmut_15': x_decimal_relative_time__mutmut_15, 
    'x_decimal_relative_time__mutmut_16': x_decimal_relative_time__mutmut_16, 
    'x_decimal_relative_time__mutmut_17': x_decimal_relative_time__mutmut_17, 
    'x_decimal_relative_time__mutmut_18': x_decimal_relative_time__mutmut_18, 
    'x_decimal_relative_time__mutmut_19': x_decimal_relative_time__mutmut_19, 
    'x_decimal_relative_time__mutmut_20': x_decimal_relative_time__mutmut_20, 
    'x_decimal_relative_time__mutmut_21': x_decimal_relative_time__mutmut_21, 
    'x_decimal_relative_time__mutmut_22': x_decimal_relative_time__mutmut_22, 
    'x_decimal_relative_time__mutmut_23': x_decimal_relative_time__mutmut_23, 
    'x_decimal_relative_time__mutmut_24': x_decimal_relative_time__mutmut_24, 
    'x_decimal_relative_time__mutmut_25': x_decimal_relative_time__mutmut_25, 
    'x_decimal_relative_time__mutmut_26': x_decimal_relative_time__mutmut_26, 
    'x_decimal_relative_time__mutmut_27': x_decimal_relative_time__mutmut_27, 
    'x_decimal_relative_time__mutmut_28': x_decimal_relative_time__mutmut_28, 
    'x_decimal_relative_time__mutmut_29': x_decimal_relative_time__mutmut_29, 
    'x_decimal_relative_time__mutmut_30': x_decimal_relative_time__mutmut_30, 
    'x_decimal_relative_time__mutmut_31': x_decimal_relative_time__mutmut_31, 
    'x_decimal_relative_time__mutmut_32': x_decimal_relative_time__mutmut_32
}

def decimal_relative_time(*args, **kwargs):
    result = _mutmut_trampoline(x_decimal_relative_time__mutmut_orig, x_decimal_relative_time__mutmut_mutants, args, kwargs)
    return result 

decimal_relative_time.__signature__ = _mutmut_signature(x_decimal_relative_time__mutmut_orig)
x_decimal_relative_time__mutmut_orig.__name__ = 'x_decimal_relative_time'


def x_relative_time__mutmut_orig(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, other, ndigits, cardinalize=True)
    phrase = 'ago'
    if drt < 0:
        phrase = 'from now'
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_1(d, other=None, ndigits=1):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, other, ndigits, cardinalize=True)
    phrase = 'ago'
    if drt < 0:
        phrase = 'from now'
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_2(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = None
    phrase = 'ago'
    if drt < 0:
        phrase = 'from now'
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_3(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(None, other, ndigits, cardinalize=True)
    phrase = 'ago'
    if drt < 0:
        phrase = 'from now'
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_4(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, None, ndigits, cardinalize=True)
    phrase = 'ago'
    if drt < 0:
        phrase = 'from now'
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_5(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, other, None, cardinalize=True)
    phrase = 'ago'
    if drt < 0:
        phrase = 'from now'
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_6(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, other, ndigits, cardinalize=None)
    phrase = 'ago'
    if drt < 0:
        phrase = 'from now'
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_7(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(other, ndigits, cardinalize=True)
    phrase = 'ago'
    if drt < 0:
        phrase = 'from now'
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_8(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, ndigits, cardinalize=True)
    phrase = 'ago'
    if drt < 0:
        phrase = 'from now'
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_9(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, other, cardinalize=True)
    phrase = 'ago'
    if drt < 0:
        phrase = 'from now'
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_10(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, other, ndigits, )
    phrase = 'ago'
    if drt < 0:
        phrase = 'from now'
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_11(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, other, ndigits, cardinalize=False)
    phrase = 'ago'
    if drt < 0:
        phrase = 'from now'
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_12(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, other, ndigits, cardinalize=True)
    phrase = None
    if drt < 0:
        phrase = 'from now'
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_13(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, other, ndigits, cardinalize=True)
    phrase = 'XXagoXX'
    if drt < 0:
        phrase = 'from now'
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_14(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, other, ndigits, cardinalize=True)
    phrase = 'AGO'
    if drt < 0:
        phrase = 'from now'
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_15(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, other, ndigits, cardinalize=True)
    phrase = 'ago'
    if drt <= 0:
        phrase = 'from now'
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_16(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, other, ndigits, cardinalize=True)
    phrase = 'ago'
    if drt < 1:
        phrase = 'from now'
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_17(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, other, ndigits, cardinalize=True)
    phrase = 'ago'
    if drt < 0:
        phrase = None
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_18(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, other, ndigits, cardinalize=True)
    phrase = 'ago'
    if drt < 0:
        phrase = 'XXfrom nowXX'
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_19(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, other, ndigits, cardinalize=True)
    phrase = 'ago'
    if drt < 0:
        phrase = 'FROM NOW'
    return f'{abs(drt):g} {unit} {phrase}'


def x_relative_time__mutmut_20(d, other=None, ndigits=0):
    """Get a string representation of the difference between two
    :class:`~datetime.datetime` objects or one
    :class:`~datetime.datetime` and the current time. Handles past and
    future times.

    Args:
        d (datetime): The first datetime object.
        other (datetime): An optional second datetime object. If
            unset, defaults to the current time as determined
            :meth:`datetime.utcnow`.
        ndigits (int): The number of decimal digits to round to,
            defaults to ``0``.
    Returns:
        A short English-language string.

    >>> now = datetime.now(timezone.utc).replace(tzinfo=None)
    >>> relative_time(now, ndigits=1)
    '0 seconds ago'
    >>> relative_time(now - timedelta(days=1, seconds=36000), ndigits=1)
    '1.4 days ago'
    >>> relative_time(now + timedelta(days=7), now, ndigits=1)
    '1 week from now'

    """
    drt, unit = decimal_relative_time(d, other, ndigits, cardinalize=True)
    phrase = 'ago'
    if drt < 0:
        phrase = 'from now'
    return f'{abs(None):g} {unit} {phrase}'

x_relative_time__mutmut_mutants : ClassVar[MutantDict] = {
'x_relative_time__mutmut_1': x_relative_time__mutmut_1, 
    'x_relative_time__mutmut_2': x_relative_time__mutmut_2, 
    'x_relative_time__mutmut_3': x_relative_time__mutmut_3, 
    'x_relative_time__mutmut_4': x_relative_time__mutmut_4, 
    'x_relative_time__mutmut_5': x_relative_time__mutmut_5, 
    'x_relative_time__mutmut_6': x_relative_time__mutmut_6, 
    'x_relative_time__mutmut_7': x_relative_time__mutmut_7, 
    'x_relative_time__mutmut_8': x_relative_time__mutmut_8, 
    'x_relative_time__mutmut_9': x_relative_time__mutmut_9, 
    'x_relative_time__mutmut_10': x_relative_time__mutmut_10, 
    'x_relative_time__mutmut_11': x_relative_time__mutmut_11, 
    'x_relative_time__mutmut_12': x_relative_time__mutmut_12, 
    'x_relative_time__mutmut_13': x_relative_time__mutmut_13, 
    'x_relative_time__mutmut_14': x_relative_time__mutmut_14, 
    'x_relative_time__mutmut_15': x_relative_time__mutmut_15, 
    'x_relative_time__mutmut_16': x_relative_time__mutmut_16, 
    'x_relative_time__mutmut_17': x_relative_time__mutmut_17, 
    'x_relative_time__mutmut_18': x_relative_time__mutmut_18, 
    'x_relative_time__mutmut_19': x_relative_time__mutmut_19, 
    'x_relative_time__mutmut_20': x_relative_time__mutmut_20
}

def relative_time(*args, **kwargs):
    result = _mutmut_trampoline(x_relative_time__mutmut_orig, x_relative_time__mutmut_mutants, args, kwargs)
    return result 

relative_time.__signature__ = _mutmut_signature(x_relative_time__mutmut_orig)
x_relative_time__mutmut_orig.__name__ = 'x_relative_time'


def x_strpdate__mutmut_orig(string, format):
    """Parse the date string according to the format in `format`.  Returns a
    :class:`date` object.  Internally, :meth:`datetime.strptime` is used to
    parse the string and thus conversion specifiers for time fields (e.g. `%H`)
    may be provided;  these will be parsed but ignored.

    Args:
        string (str): The date string to be parsed.
        format (str): The `strptime`_-style date format string.
    Returns:
        datetime.date

    .. _`strptime`: https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior

    >>> strpdate('2016-02-14', '%Y-%m-%d')
    datetime.date(2016, 2, 14)
    >>> strpdate('26/12 (2015)', '%d/%m (%Y)')
    datetime.date(2015, 12, 26)
    >>> strpdate('20151231 23:59:59', '%Y%m%d %H:%M:%S')
    datetime.date(2015, 12, 31)
    >>> strpdate('20160101 00:00:00.001', '%Y%m%d %H:%M:%S.%f')
    datetime.date(2016, 1, 1)
    """
    whence = datetime.strptime(string, format)
    return whence.date()


def x_strpdate__mutmut_1(string, format):
    """Parse the date string according to the format in `format`.  Returns a
    :class:`date` object.  Internally, :meth:`datetime.strptime` is used to
    parse the string and thus conversion specifiers for time fields (e.g. `%H`)
    may be provided;  these will be parsed but ignored.

    Args:
        string (str): The date string to be parsed.
        format (str): The `strptime`_-style date format string.
    Returns:
        datetime.date

    .. _`strptime`: https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior

    >>> strpdate('2016-02-14', '%Y-%m-%d')
    datetime.date(2016, 2, 14)
    >>> strpdate('26/12 (2015)', '%d/%m (%Y)')
    datetime.date(2015, 12, 26)
    >>> strpdate('20151231 23:59:59', '%Y%m%d %H:%M:%S')
    datetime.date(2015, 12, 31)
    >>> strpdate('20160101 00:00:00.001', '%Y%m%d %H:%M:%S.%f')
    datetime.date(2016, 1, 1)
    """
    whence = None
    return whence.date()


def x_strpdate__mutmut_2(string, format):
    """Parse the date string according to the format in `format`.  Returns a
    :class:`date` object.  Internally, :meth:`datetime.strptime` is used to
    parse the string and thus conversion specifiers for time fields (e.g. `%H`)
    may be provided;  these will be parsed but ignored.

    Args:
        string (str): The date string to be parsed.
        format (str): The `strptime`_-style date format string.
    Returns:
        datetime.date

    .. _`strptime`: https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior

    >>> strpdate('2016-02-14', '%Y-%m-%d')
    datetime.date(2016, 2, 14)
    >>> strpdate('26/12 (2015)', '%d/%m (%Y)')
    datetime.date(2015, 12, 26)
    >>> strpdate('20151231 23:59:59', '%Y%m%d %H:%M:%S')
    datetime.date(2015, 12, 31)
    >>> strpdate('20160101 00:00:00.001', '%Y%m%d %H:%M:%S.%f')
    datetime.date(2016, 1, 1)
    """
    whence = datetime.strptime(None, format)
    return whence.date()


def x_strpdate__mutmut_3(string, format):
    """Parse the date string according to the format in `format`.  Returns a
    :class:`date` object.  Internally, :meth:`datetime.strptime` is used to
    parse the string and thus conversion specifiers for time fields (e.g. `%H`)
    may be provided;  these will be parsed but ignored.

    Args:
        string (str): The date string to be parsed.
        format (str): The `strptime`_-style date format string.
    Returns:
        datetime.date

    .. _`strptime`: https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior

    >>> strpdate('2016-02-14', '%Y-%m-%d')
    datetime.date(2016, 2, 14)
    >>> strpdate('26/12 (2015)', '%d/%m (%Y)')
    datetime.date(2015, 12, 26)
    >>> strpdate('20151231 23:59:59', '%Y%m%d %H:%M:%S')
    datetime.date(2015, 12, 31)
    >>> strpdate('20160101 00:00:00.001', '%Y%m%d %H:%M:%S.%f')
    datetime.date(2016, 1, 1)
    """
    whence = datetime.strptime(string, None)
    return whence.date()


def x_strpdate__mutmut_4(string, format):
    """Parse the date string according to the format in `format`.  Returns a
    :class:`date` object.  Internally, :meth:`datetime.strptime` is used to
    parse the string and thus conversion specifiers for time fields (e.g. `%H`)
    may be provided;  these will be parsed but ignored.

    Args:
        string (str): The date string to be parsed.
        format (str): The `strptime`_-style date format string.
    Returns:
        datetime.date

    .. _`strptime`: https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior

    >>> strpdate('2016-02-14', '%Y-%m-%d')
    datetime.date(2016, 2, 14)
    >>> strpdate('26/12 (2015)', '%d/%m (%Y)')
    datetime.date(2015, 12, 26)
    >>> strpdate('20151231 23:59:59', '%Y%m%d %H:%M:%S')
    datetime.date(2015, 12, 31)
    >>> strpdate('20160101 00:00:00.001', '%Y%m%d %H:%M:%S.%f')
    datetime.date(2016, 1, 1)
    """
    whence = datetime.strptime(format)
    return whence.date()


def x_strpdate__mutmut_5(string, format):
    """Parse the date string according to the format in `format`.  Returns a
    :class:`date` object.  Internally, :meth:`datetime.strptime` is used to
    parse the string and thus conversion specifiers for time fields (e.g. `%H`)
    may be provided;  these will be parsed but ignored.

    Args:
        string (str): The date string to be parsed.
        format (str): The `strptime`_-style date format string.
    Returns:
        datetime.date

    .. _`strptime`: https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior

    >>> strpdate('2016-02-14', '%Y-%m-%d')
    datetime.date(2016, 2, 14)
    >>> strpdate('26/12 (2015)', '%d/%m (%Y)')
    datetime.date(2015, 12, 26)
    >>> strpdate('20151231 23:59:59', '%Y%m%d %H:%M:%S')
    datetime.date(2015, 12, 31)
    >>> strpdate('20160101 00:00:00.001', '%Y%m%d %H:%M:%S.%f')
    datetime.date(2016, 1, 1)
    """
    whence = datetime.strptime(string, )
    return whence.date()

x_strpdate__mutmut_mutants : ClassVar[MutantDict] = {
'x_strpdate__mutmut_1': x_strpdate__mutmut_1, 
    'x_strpdate__mutmut_2': x_strpdate__mutmut_2, 
    'x_strpdate__mutmut_3': x_strpdate__mutmut_3, 
    'x_strpdate__mutmut_4': x_strpdate__mutmut_4, 
    'x_strpdate__mutmut_5': x_strpdate__mutmut_5
}

def strpdate(*args, **kwargs):
    result = _mutmut_trampoline(x_strpdate__mutmut_orig, x_strpdate__mutmut_mutants, args, kwargs)
    return result 

strpdate.__signature__ = _mutmut_signature(x_strpdate__mutmut_orig)
x_strpdate__mutmut_orig.__name__ = 'x_strpdate'


def x_daterange__mutmut_orig(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_1(start, stop, step=2, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_2(start, stop, step=1, inclusive=True):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_3(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_4(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError(None)
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_5(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("XXstart expected datetime.date instanceXX")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_6(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("START EXPECTED DATETIME.DATE INSTANCE")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_7(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop or not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_8(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_9(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError(None)
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_10(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("XXstop expected datetime.date instance or NoneXX")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_11(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or none")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_12(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("STOP EXPECTED DATETIME.DATE INSTANCE OR NONE")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_13(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = None
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_14(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = None
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_15(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 1, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_16(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 1, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_17(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = None
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_18(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(None), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_19(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(None)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_20(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = None
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_21(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=None)
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_22(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(None))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_23(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError(None)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_24(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' / step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_25(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('XXstep expected int, timedelta, or tupleXX'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_26(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('STEP EXPECTED INT, TIMEDELTA, OR TUPLE'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_27(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         'XX (year, month, day), not: %rXX' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_28(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (YEAR, MONTH, DAY), NOT: %R' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_29(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step = y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_30(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step -= y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_31(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step / 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_32(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 13

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_33(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is not None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_34(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = None
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_35(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: None
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_36(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: True
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_37(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start < stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_38(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = None
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_39(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = None
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_40(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = None

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_41(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_42(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(None, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_43(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, None):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_44(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_45(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, ):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_46(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = None
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_47(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod(None, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_48(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, None)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_49(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod(12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_50(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, )
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_51(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) - m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_52(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month + 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_53(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 2) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_54(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 13)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_55(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = None
        now = now + d_step
    return


def x_daterange__mutmut_56(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=None,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_57(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=None)
        now = now + d_step
    return


def x_daterange__mutmut_58(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_59(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              )
        now = now + d_step
    return


def x_daterange__mutmut_60(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year - m_y_step,
                              month=(cur_month + 1))
        now = now + d_step
    return


def x_daterange__mutmut_61(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month - 1))
        now = now + d_step
    return


def x_daterange__mutmut_62(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 2))
        now = now + d_step
    return


def x_daterange__mutmut_63(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = None
    return


def x_daterange__mutmut_64(start, stop, step=1, inclusive=False):
    """In the spirit of :func:`range` and :func:`xrange`, the `daterange`
    generator that yields a sequence of :class:`~datetime.date`
    objects, starting at *start*, incrementing by *step*, until *stop*
    is reached.

    When *inclusive* is True, the final date may be *stop*, **if**
    *step* falls evenly on it. By default, *step* is one day. See
    details below for many more details.

    Args:
        start (datetime.date): The starting date The first value in
            the sequence.
        stop (datetime.date): The stopping date. By default not
            included in return. Can be `None` to yield an infinite
            sequence.
        step (int): The value to increment *start* by to reach
            *stop*. Can be an :class:`int` number of days, a
            :class:`datetime.timedelta`, or a :class:`tuple` of integers,
            `(year, month, day)`. Positive and negative *step* values
            are supported.
        inclusive (bool): Whether or not the *stop* date can be
            returned. *stop* is only returned when a *step* falls evenly
            on it.

    >>> christmas = date(year=2015, month=12, day=25)
    >>> boxing_day = date(year=2015, month=12, day=26)
    >>> new_year = date(year=2016, month=1,  day=1)
    >>> for day in daterange(christmas, new_year):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    datetime.date(2015, 12, 26)
    datetime.date(2015, 12, 27)
    datetime.date(2015, 12, 28)
    datetime.date(2015, 12, 29)
    datetime.date(2015, 12, 30)
    datetime.date(2015, 12, 31)
    >>> for day in daterange(christmas, boxing_day):
    ...     print(repr(day))
    datetime.date(2015, 12, 25)
    >>> for day in daterange(date(2017, 5, 1), date(2017, 8, 1),
    ...                      step=(0, 1, 0), inclusive=True):
    ...     print(repr(day))
    datetime.date(2017, 5, 1)
    datetime.date(2017, 6, 1)
    datetime.date(2017, 7, 1)
    datetime.date(2017, 8, 1)

    *Be careful when using stop=None, as this will yield an infinite
    sequence of dates.*
    """
    if not isinstance(start, date):
        raise TypeError("start expected datetime.date instance")
    if stop and not isinstance(stop, date):
        raise TypeError("stop expected datetime.date instance or None")
    try:
        y_step, m_step, d_step = step
    except TypeError:
        y_step, m_step, d_step = 0, 0, step
    else:
        y_step, m_step = int(y_step), int(m_step)
    if isinstance(d_step, int):
        d_step = timedelta(days=int(d_step))
    elif isinstance(d_step, timedelta):
        pass
    else:
        raise ValueError('step expected int, timedelta, or tuple'
                         ' (year, month, day), not: %r' % step)
    
    m_step += y_step * 12

    if stop is None:
        finished = lambda now, stop: False
    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge
    else:
        finished = operator.lt if inclusive else operator.le
    now = start

    while not finished(now, stop):
        yield now
        if m_step:
            m_y_step, cur_month = divmod((now.month - 1) + m_step, 12)
            now = now.replace(year=now.year + m_y_step,
                              month=(cur_month + 1))
        now = now - d_step
    return

x_daterange__mutmut_mutants : ClassVar[MutantDict] = {
'x_daterange__mutmut_1': x_daterange__mutmut_1, 
    'x_daterange__mutmut_2': x_daterange__mutmut_2, 
    'x_daterange__mutmut_3': x_daterange__mutmut_3, 
    'x_daterange__mutmut_4': x_daterange__mutmut_4, 
    'x_daterange__mutmut_5': x_daterange__mutmut_5, 
    'x_daterange__mutmut_6': x_daterange__mutmut_6, 
    'x_daterange__mutmut_7': x_daterange__mutmut_7, 
    'x_daterange__mutmut_8': x_daterange__mutmut_8, 
    'x_daterange__mutmut_9': x_daterange__mutmut_9, 
    'x_daterange__mutmut_10': x_daterange__mutmut_10, 
    'x_daterange__mutmut_11': x_daterange__mutmut_11, 
    'x_daterange__mutmut_12': x_daterange__mutmut_12, 
    'x_daterange__mutmut_13': x_daterange__mutmut_13, 
    'x_daterange__mutmut_14': x_daterange__mutmut_14, 
    'x_daterange__mutmut_15': x_daterange__mutmut_15, 
    'x_daterange__mutmut_16': x_daterange__mutmut_16, 
    'x_daterange__mutmut_17': x_daterange__mutmut_17, 
    'x_daterange__mutmut_18': x_daterange__mutmut_18, 
    'x_daterange__mutmut_19': x_daterange__mutmut_19, 
    'x_daterange__mutmut_20': x_daterange__mutmut_20, 
    'x_daterange__mutmut_21': x_daterange__mutmut_21, 
    'x_daterange__mutmut_22': x_daterange__mutmut_22, 
    'x_daterange__mutmut_23': x_daterange__mutmut_23, 
    'x_daterange__mutmut_24': x_daterange__mutmut_24, 
    'x_daterange__mutmut_25': x_daterange__mutmut_25, 
    'x_daterange__mutmut_26': x_daterange__mutmut_26, 
    'x_daterange__mutmut_27': x_daterange__mutmut_27, 
    'x_daterange__mutmut_28': x_daterange__mutmut_28, 
    'x_daterange__mutmut_29': x_daterange__mutmut_29, 
    'x_daterange__mutmut_30': x_daterange__mutmut_30, 
    'x_daterange__mutmut_31': x_daterange__mutmut_31, 
    'x_daterange__mutmut_32': x_daterange__mutmut_32, 
    'x_daterange__mutmut_33': x_daterange__mutmut_33, 
    'x_daterange__mutmut_34': x_daterange__mutmut_34, 
    'x_daterange__mutmut_35': x_daterange__mutmut_35, 
    'x_daterange__mutmut_36': x_daterange__mutmut_36, 
    'x_daterange__mutmut_37': x_daterange__mutmut_37, 
    'x_daterange__mutmut_38': x_daterange__mutmut_38, 
    'x_daterange__mutmut_39': x_daterange__mutmut_39, 
    'x_daterange__mutmut_40': x_daterange__mutmut_40, 
    'x_daterange__mutmut_41': x_daterange__mutmut_41, 
    'x_daterange__mutmut_42': x_daterange__mutmut_42, 
    'x_daterange__mutmut_43': x_daterange__mutmut_43, 
    'x_daterange__mutmut_44': x_daterange__mutmut_44, 
    'x_daterange__mutmut_45': x_daterange__mutmut_45, 
    'x_daterange__mutmut_46': x_daterange__mutmut_46, 
    'x_daterange__mutmut_47': x_daterange__mutmut_47, 
    'x_daterange__mutmut_48': x_daterange__mutmut_48, 
    'x_daterange__mutmut_49': x_daterange__mutmut_49, 
    'x_daterange__mutmut_50': x_daterange__mutmut_50, 
    'x_daterange__mutmut_51': x_daterange__mutmut_51, 
    'x_daterange__mutmut_52': x_daterange__mutmut_52, 
    'x_daterange__mutmut_53': x_daterange__mutmut_53, 
    'x_daterange__mutmut_54': x_daterange__mutmut_54, 
    'x_daterange__mutmut_55': x_daterange__mutmut_55, 
    'x_daterange__mutmut_56': x_daterange__mutmut_56, 
    'x_daterange__mutmut_57': x_daterange__mutmut_57, 
    'x_daterange__mutmut_58': x_daterange__mutmut_58, 
    'x_daterange__mutmut_59': x_daterange__mutmut_59, 
    'x_daterange__mutmut_60': x_daterange__mutmut_60, 
    'x_daterange__mutmut_61': x_daterange__mutmut_61, 
    'x_daterange__mutmut_62': x_daterange__mutmut_62, 
    'x_daterange__mutmut_63': x_daterange__mutmut_63, 
    'x_daterange__mutmut_64': x_daterange__mutmut_64
}

def daterange(*args, **kwargs):
    result = _mutmut_trampoline(x_daterange__mutmut_orig, x_daterange__mutmut_mutants, args, kwargs)
    return result 

daterange.__signature__ = _mutmut_signature(x_daterange__mutmut_orig)
x_daterange__mutmut_orig.__name__ = 'x_daterange'


# Timezone support (brought in from tzutils)


ZERO = timedelta(0)
HOUR = timedelta(hours=1)


class ConstantTZInfo(tzinfo):
    """
    A :class:`~datetime.tzinfo` subtype whose *offset* remains constant
    (no daylight savings).

    Args:
        name (str): Name of the timezone.
        offset (datetime.timedelta): Offset of the timezone.
    """
    def xǁConstantTZInfoǁ__init____mutmut_orig(self, name="ConstantTZ", offset=ZERO):
        self.name = name
        self.offset = offset
    def xǁConstantTZInfoǁ__init____mutmut_1(self, name="XXConstantTZXX", offset=ZERO):
        self.name = name
        self.offset = offset
    def xǁConstantTZInfoǁ__init____mutmut_2(self, name="constanttz", offset=ZERO):
        self.name = name
        self.offset = offset
    def xǁConstantTZInfoǁ__init____mutmut_3(self, name="CONSTANTTZ", offset=ZERO):
        self.name = name
        self.offset = offset
    def xǁConstantTZInfoǁ__init____mutmut_4(self, name="ConstantTZ", offset=ZERO):
        self.name = None
        self.offset = offset
    def xǁConstantTZInfoǁ__init____mutmut_5(self, name="ConstantTZ", offset=ZERO):
        self.name = name
        self.offset = None
    
    xǁConstantTZInfoǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁConstantTZInfoǁ__init____mutmut_1': xǁConstantTZInfoǁ__init____mutmut_1, 
        'xǁConstantTZInfoǁ__init____mutmut_2': xǁConstantTZInfoǁ__init____mutmut_2, 
        'xǁConstantTZInfoǁ__init____mutmut_3': xǁConstantTZInfoǁ__init____mutmut_3, 
        'xǁConstantTZInfoǁ__init____mutmut_4': xǁConstantTZInfoǁ__init____mutmut_4, 
        'xǁConstantTZInfoǁ__init____mutmut_5': xǁConstantTZInfoǁ__init____mutmut_5
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁConstantTZInfoǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁConstantTZInfoǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁConstantTZInfoǁ__init____mutmut_orig)
    xǁConstantTZInfoǁ__init____mutmut_orig.__name__ = 'xǁConstantTZInfoǁ__init__'

    @property
    def utcoffset_hours(self):
        return timedelta.total_seconds(self.offset) / (60 * 60)

    def utcoffset(self, dt):
        return self.offset

    def tzname(self, dt):
        return self.name

    def dst(self, dt):
        return ZERO

    def xǁConstantTZInfoǁ__repr____mutmut_orig(self):
        cn = self.__class__.__name__
        return f'{cn}(name={self.name!r}, offset={self.offset!r})'

    def xǁConstantTZInfoǁ__repr____mutmut_1(self):
        cn = None
        return f'{cn}(name={self.name!r}, offset={self.offset!r})'
    
    xǁConstantTZInfoǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁConstantTZInfoǁ__repr____mutmut_1': xǁConstantTZInfoǁ__repr____mutmut_1
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁConstantTZInfoǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁConstantTZInfoǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁConstantTZInfoǁ__repr____mutmut_orig)
    xǁConstantTZInfoǁ__repr____mutmut_orig.__name__ = 'xǁConstantTZInfoǁ__repr__'


UTC = ConstantTZInfo('UTC')
EPOCH_AWARE = datetime.fromtimestamp(0, UTC)


class LocalTZInfo(tzinfo):
    """The ``LocalTZInfo`` type takes data available in the time module
    about the local timezone and makes a practical
    :class:`datetime.tzinfo` to represent the timezone settings of the
    operating system.

    For a more in-depth integration with the operating system, check
    out `tzlocal`_. It builds on `pytz`_ and implements heuristics for
    many versions of major operating systems to provide the official
    ``pytz`` tzinfo, instead of the LocalTZ generalization.

    .. _tzlocal: https://pypi.python.org/pypi/tzlocal
    .. _pytz: https://pypi.python.org/pypi/pytz

    """
    _std_offset = timedelta(seconds=-time.timezone)
    _dst_offset = _std_offset
    if time.daylight:
        _dst_offset = timedelta(seconds=-time.altzone)

    def xǁLocalTZInfoǁis_dst__mutmut_orig(self, dt):
        dt_t = (dt.year, dt.month, dt.day, dt.hour, dt.minute,
                dt.second, dt.weekday(), 0, -1)
        local_t = time.localtime(time.mktime(dt_t))
        return local_t.tm_isdst > 0

    def xǁLocalTZInfoǁis_dst__mutmut_1(self, dt):
        dt_t = None
        local_t = time.localtime(time.mktime(dt_t))
        return local_t.tm_isdst > 0

    def xǁLocalTZInfoǁis_dst__mutmut_2(self, dt):
        dt_t = (dt.year, dt.month, dt.day, dt.hour, dt.minute,
                dt.second, dt.weekday(), 1, -1)
        local_t = time.localtime(time.mktime(dt_t))
        return local_t.tm_isdst > 0

    def xǁLocalTZInfoǁis_dst__mutmut_3(self, dt):
        dt_t = (dt.year, dt.month, dt.day, dt.hour, dt.minute,
                dt.second, dt.weekday(), 0, +1)
        local_t = time.localtime(time.mktime(dt_t))
        return local_t.tm_isdst > 0

    def xǁLocalTZInfoǁis_dst__mutmut_4(self, dt):
        dt_t = (dt.year, dt.month, dt.day, dt.hour, dt.minute,
                dt.second, dt.weekday(), 0, -2)
        local_t = time.localtime(time.mktime(dt_t))
        return local_t.tm_isdst > 0

    def xǁLocalTZInfoǁis_dst__mutmut_5(self, dt):
        dt_t = (dt.year, dt.month, dt.day, dt.hour, dt.minute,
                dt.second, dt.weekday(), 0, -1)
        local_t = None
        return local_t.tm_isdst > 0

    def xǁLocalTZInfoǁis_dst__mutmut_6(self, dt):
        dt_t = (dt.year, dt.month, dt.day, dt.hour, dt.minute,
                dt.second, dt.weekday(), 0, -1)
        local_t = time.localtime(None)
        return local_t.tm_isdst > 0

    def xǁLocalTZInfoǁis_dst__mutmut_7(self, dt):
        dt_t = (dt.year, dt.month, dt.day, dt.hour, dt.minute,
                dt.second, dt.weekday(), 0, -1)
        local_t = time.localtime(time.mktime(None))
        return local_t.tm_isdst > 0

    def xǁLocalTZInfoǁis_dst__mutmut_8(self, dt):
        dt_t = (dt.year, dt.month, dt.day, dt.hour, dt.minute,
                dt.second, dt.weekday(), 0, -1)
        local_t = time.localtime(time.mktime(dt_t))
        return local_t.tm_isdst >= 0

    def xǁLocalTZInfoǁis_dst__mutmut_9(self, dt):
        dt_t = (dt.year, dt.month, dt.day, dt.hour, dt.minute,
                dt.second, dt.weekday(), 0, -1)
        local_t = time.localtime(time.mktime(dt_t))
        return local_t.tm_isdst > 1
    
    xǁLocalTZInfoǁis_dst__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLocalTZInfoǁis_dst__mutmut_1': xǁLocalTZInfoǁis_dst__mutmut_1, 
        'xǁLocalTZInfoǁis_dst__mutmut_2': xǁLocalTZInfoǁis_dst__mutmut_2, 
        'xǁLocalTZInfoǁis_dst__mutmut_3': xǁLocalTZInfoǁis_dst__mutmut_3, 
        'xǁLocalTZInfoǁis_dst__mutmut_4': xǁLocalTZInfoǁis_dst__mutmut_4, 
        'xǁLocalTZInfoǁis_dst__mutmut_5': xǁLocalTZInfoǁis_dst__mutmut_5, 
        'xǁLocalTZInfoǁis_dst__mutmut_6': xǁLocalTZInfoǁis_dst__mutmut_6, 
        'xǁLocalTZInfoǁis_dst__mutmut_7': xǁLocalTZInfoǁis_dst__mutmut_7, 
        'xǁLocalTZInfoǁis_dst__mutmut_8': xǁLocalTZInfoǁis_dst__mutmut_8, 
        'xǁLocalTZInfoǁis_dst__mutmut_9': xǁLocalTZInfoǁis_dst__mutmut_9
    }
    
    def is_dst(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLocalTZInfoǁis_dst__mutmut_orig"), object.__getattribute__(self, "xǁLocalTZInfoǁis_dst__mutmut_mutants"), args, kwargs, self)
        return result 
    
    is_dst.__signature__ = _mutmut_signature(xǁLocalTZInfoǁis_dst__mutmut_orig)
    xǁLocalTZInfoǁis_dst__mutmut_orig.__name__ = 'xǁLocalTZInfoǁis_dst'

    def xǁLocalTZInfoǁutcoffset__mutmut_orig(self, dt):
        if self.is_dst(dt):
            return self._dst_offset
        return self._std_offset

    def xǁLocalTZInfoǁutcoffset__mutmut_1(self, dt):
        if self.is_dst(None):
            return self._dst_offset
        return self._std_offset
    
    xǁLocalTZInfoǁutcoffset__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLocalTZInfoǁutcoffset__mutmut_1': xǁLocalTZInfoǁutcoffset__mutmut_1
    }
    
    def utcoffset(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLocalTZInfoǁutcoffset__mutmut_orig"), object.__getattribute__(self, "xǁLocalTZInfoǁutcoffset__mutmut_mutants"), args, kwargs, self)
        return result 
    
    utcoffset.__signature__ = _mutmut_signature(xǁLocalTZInfoǁutcoffset__mutmut_orig)
    xǁLocalTZInfoǁutcoffset__mutmut_orig.__name__ = 'xǁLocalTZInfoǁutcoffset'

    def xǁLocalTZInfoǁdst__mutmut_orig(self, dt):
        if self.is_dst(dt):
            return self._dst_offset - self._std_offset
        return ZERO

    def xǁLocalTZInfoǁdst__mutmut_1(self, dt):
        if self.is_dst(None):
            return self._dst_offset - self._std_offset
        return ZERO

    def xǁLocalTZInfoǁdst__mutmut_2(self, dt):
        if self.is_dst(dt):
            return self._dst_offset + self._std_offset
        return ZERO
    
    xǁLocalTZInfoǁdst__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLocalTZInfoǁdst__mutmut_1': xǁLocalTZInfoǁdst__mutmut_1, 
        'xǁLocalTZInfoǁdst__mutmut_2': xǁLocalTZInfoǁdst__mutmut_2
    }
    
    def dst(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLocalTZInfoǁdst__mutmut_orig"), object.__getattribute__(self, "xǁLocalTZInfoǁdst__mutmut_mutants"), args, kwargs, self)
        return result 
    
    dst.__signature__ = _mutmut_signature(xǁLocalTZInfoǁdst__mutmut_orig)
    xǁLocalTZInfoǁdst__mutmut_orig.__name__ = 'xǁLocalTZInfoǁdst'

    def xǁLocalTZInfoǁtzname__mutmut_orig(self, dt):
        return time.tzname[self.is_dst(dt)]

    def xǁLocalTZInfoǁtzname__mutmut_1(self, dt):
        return time.tzname[self.is_dst(None)]
    
    xǁLocalTZInfoǁtzname__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLocalTZInfoǁtzname__mutmut_1': xǁLocalTZInfoǁtzname__mutmut_1
    }
    
    def tzname(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLocalTZInfoǁtzname__mutmut_orig"), object.__getattribute__(self, "xǁLocalTZInfoǁtzname__mutmut_mutants"), args, kwargs, self)
        return result 
    
    tzname.__signature__ = _mutmut_signature(xǁLocalTZInfoǁtzname__mutmut_orig)
    xǁLocalTZInfoǁtzname__mutmut_orig.__name__ = 'xǁLocalTZInfoǁtzname'

    def xǁLocalTZInfoǁ__repr____mutmut_orig(self):
        return '%s()' % self.__class__.__name__

    def xǁLocalTZInfoǁ__repr____mutmut_1(self):
        return '%s()' / self.__class__.__name__

    def xǁLocalTZInfoǁ__repr____mutmut_2(self):
        return 'XX%s()XX' % self.__class__.__name__

    def xǁLocalTZInfoǁ__repr____mutmut_3(self):
        return '%S()' % self.__class__.__name__
    
    xǁLocalTZInfoǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁLocalTZInfoǁ__repr____mutmut_1': xǁLocalTZInfoǁ__repr____mutmut_1, 
        'xǁLocalTZInfoǁ__repr____mutmut_2': xǁLocalTZInfoǁ__repr____mutmut_2, 
        'xǁLocalTZInfoǁ__repr____mutmut_3': xǁLocalTZInfoǁ__repr____mutmut_3
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁLocalTZInfoǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁLocalTZInfoǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁLocalTZInfoǁ__repr____mutmut_orig)
    xǁLocalTZInfoǁ__repr____mutmut_orig.__name__ = 'xǁLocalTZInfoǁ__repr__'


LocalTZ = LocalTZInfo()


def x__first_sunday_on_or_after__mutmut_orig(dt):
    days_to_go = 6 - dt.weekday()
    if days_to_go:
        dt += timedelta(days_to_go)
    return dt


def x__first_sunday_on_or_after__mutmut_1(dt):
    days_to_go = None
    if days_to_go:
        dt += timedelta(days_to_go)
    return dt


def x__first_sunday_on_or_after__mutmut_2(dt):
    days_to_go = 6 + dt.weekday()
    if days_to_go:
        dt += timedelta(days_to_go)
    return dt


def x__first_sunday_on_or_after__mutmut_3(dt):
    days_to_go = 7 - dt.weekday()
    if days_to_go:
        dt += timedelta(days_to_go)
    return dt


def x__first_sunday_on_or_after__mutmut_4(dt):
    days_to_go = 6 - dt.weekday()
    if days_to_go:
        dt = timedelta(days_to_go)
    return dt


def x__first_sunday_on_or_after__mutmut_5(dt):
    days_to_go = 6 - dt.weekday()
    if days_to_go:
        dt -= timedelta(days_to_go)
    return dt


def x__first_sunday_on_or_after__mutmut_6(dt):
    days_to_go = 6 - dt.weekday()
    if days_to_go:
        dt += timedelta(None)
    return dt

x__first_sunday_on_or_after__mutmut_mutants : ClassVar[MutantDict] = {
'x__first_sunday_on_or_after__mutmut_1': x__first_sunday_on_or_after__mutmut_1, 
    'x__first_sunday_on_or_after__mutmut_2': x__first_sunday_on_or_after__mutmut_2, 
    'x__first_sunday_on_or_after__mutmut_3': x__first_sunday_on_or_after__mutmut_3, 
    'x__first_sunday_on_or_after__mutmut_4': x__first_sunday_on_or_after__mutmut_4, 
    'x__first_sunday_on_or_after__mutmut_5': x__first_sunday_on_or_after__mutmut_5, 
    'x__first_sunday_on_or_after__mutmut_6': x__first_sunday_on_or_after__mutmut_6
}

def _first_sunday_on_or_after(*args, **kwargs):
    result = _mutmut_trampoline(x__first_sunday_on_or_after__mutmut_orig, x__first_sunday_on_or_after__mutmut_mutants, args, kwargs)
    return result 

_first_sunday_on_or_after.__signature__ = _mutmut_signature(x__first_sunday_on_or_after__mutmut_orig)
x__first_sunday_on_or_after__mutmut_orig.__name__ = 'x__first_sunday_on_or_after'


# US DST Rules
#
# This is a simplified (i.e., wrong for a few cases) set of rules for US
# DST start and end times. For a complete and up-to-date set of DST rules
# and timezone definitions, visit the Olson Database (or try pytz):
# http://www.twinsun.com/tz/tz-link.htm
# http://sourceforge.net/projects/pytz/ (might not be up-to-date)
#
# In the US, since 2007, DST starts at 2am (standard time) on the second
# Sunday in March, which is the first Sunday on or after Mar 8.
DSTSTART_2007 = datetime(1, 3, 8, 2)
# and ends at 2am (DST time; 1am standard time) on the first Sunday of Nov.
DSTEND_2007 = datetime(1, 11, 1, 1)
# From 1987 to 2006, DST used to start at 2am (standard time) on the first
# Sunday in April and to end at 2am (DST time; 1am standard time) on the last
# Sunday of October, which is the first Sunday on or after Oct 25.
DSTSTART_1987_2006 = datetime(1, 4, 1, 2)
DSTEND_1987_2006 = datetime(1, 10, 25, 1)
# From 1967 to 1986, DST used to start at 2am (standard time) on the last
# Sunday in April (the one on or after April 24) and to end at 2am (DST time;
# 1am standard time) on the last Sunday of October, which is the first Sunday
# on or after Oct 25.
DSTSTART_1967_1986 = datetime(1, 4, 24, 2)
DSTEND_1967_1986 = DSTEND_1987_2006


class USTimeZone(tzinfo):
    """Copied directly from the Python docs, the ``USTimeZone`` is a
    :class:`datetime.tzinfo` subtype used to create the
    :data:`Eastern`, :data:`Central`, :data:`Mountain`, and
    :data:`Pacific` tzinfo types.
    """
    def xǁUSTimeZoneǁ__init____mutmut_orig(self, hours, reprname, stdname, dstname):
        self.stdoffset = timedelta(hours=hours)
        self.reprname = reprname
        self.stdname = stdname
        self.dstname = dstname
    def xǁUSTimeZoneǁ__init____mutmut_1(self, hours, reprname, stdname, dstname):
        self.stdoffset = None
        self.reprname = reprname
        self.stdname = stdname
        self.dstname = dstname
    def xǁUSTimeZoneǁ__init____mutmut_2(self, hours, reprname, stdname, dstname):
        self.stdoffset = timedelta(hours=None)
        self.reprname = reprname
        self.stdname = stdname
        self.dstname = dstname
    def xǁUSTimeZoneǁ__init____mutmut_3(self, hours, reprname, stdname, dstname):
        self.stdoffset = timedelta(hours=hours)
        self.reprname = None
        self.stdname = stdname
        self.dstname = dstname
    def xǁUSTimeZoneǁ__init____mutmut_4(self, hours, reprname, stdname, dstname):
        self.stdoffset = timedelta(hours=hours)
        self.reprname = reprname
        self.stdname = None
        self.dstname = dstname
    def xǁUSTimeZoneǁ__init____mutmut_5(self, hours, reprname, stdname, dstname):
        self.stdoffset = timedelta(hours=hours)
        self.reprname = reprname
        self.stdname = stdname
        self.dstname = None
    
    xǁUSTimeZoneǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁUSTimeZoneǁ__init____mutmut_1': xǁUSTimeZoneǁ__init____mutmut_1, 
        'xǁUSTimeZoneǁ__init____mutmut_2': xǁUSTimeZoneǁ__init____mutmut_2, 
        'xǁUSTimeZoneǁ__init____mutmut_3': xǁUSTimeZoneǁ__init____mutmut_3, 
        'xǁUSTimeZoneǁ__init____mutmut_4': xǁUSTimeZoneǁ__init____mutmut_4, 
        'xǁUSTimeZoneǁ__init____mutmut_5': xǁUSTimeZoneǁ__init____mutmut_5
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁUSTimeZoneǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁUSTimeZoneǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁUSTimeZoneǁ__init____mutmut_orig)
    xǁUSTimeZoneǁ__init____mutmut_orig.__name__ = 'xǁUSTimeZoneǁ__init__'

    def __repr__(self):
        return self.reprname

    def xǁUSTimeZoneǁtzname__mutmut_orig(self, dt):
        if self.dst(dt):
            return self.dstname
        else:
            return self.stdname

    def xǁUSTimeZoneǁtzname__mutmut_1(self, dt):
        if self.dst(None):
            return self.dstname
        else:
            return self.stdname
    
    xǁUSTimeZoneǁtzname__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁUSTimeZoneǁtzname__mutmut_1': xǁUSTimeZoneǁtzname__mutmut_1
    }
    
    def tzname(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁUSTimeZoneǁtzname__mutmut_orig"), object.__getattribute__(self, "xǁUSTimeZoneǁtzname__mutmut_mutants"), args, kwargs, self)
        return result 
    
    tzname.__signature__ = _mutmut_signature(xǁUSTimeZoneǁtzname__mutmut_orig)
    xǁUSTimeZoneǁtzname__mutmut_orig.__name__ = 'xǁUSTimeZoneǁtzname'

    def xǁUSTimeZoneǁutcoffset__mutmut_orig(self, dt):
        return self.stdoffset + self.dst(dt)

    def xǁUSTimeZoneǁutcoffset__mutmut_1(self, dt):
        return self.stdoffset - self.dst(dt)

    def xǁUSTimeZoneǁutcoffset__mutmut_2(self, dt):
        return self.stdoffset + self.dst(None)
    
    xǁUSTimeZoneǁutcoffset__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁUSTimeZoneǁutcoffset__mutmut_1': xǁUSTimeZoneǁutcoffset__mutmut_1, 
        'xǁUSTimeZoneǁutcoffset__mutmut_2': xǁUSTimeZoneǁutcoffset__mutmut_2
    }
    
    def utcoffset(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁUSTimeZoneǁutcoffset__mutmut_orig"), object.__getattribute__(self, "xǁUSTimeZoneǁutcoffset__mutmut_mutants"), args, kwargs, self)
        return result 
    
    utcoffset.__signature__ = _mutmut_signature(xǁUSTimeZoneǁutcoffset__mutmut_orig)
    xǁUSTimeZoneǁutcoffset__mutmut_orig.__name__ = 'xǁUSTimeZoneǁutcoffset'

    def xǁUSTimeZoneǁdst__mutmut_orig(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_1(self, dt):
        if dt is None and dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_2(self, dt):
        if dt is not None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_3(self, dt):
        if dt is None or dt.tzinfo is not None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_4(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is not self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_5(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2007 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_6(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 <= dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_7(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = None
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_8(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1987 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_9(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 <= dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_10(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year <= 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_11(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2008:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_12(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = None
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_13(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1967 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_14(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 <= dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_15(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year <= 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_16(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1988:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_17(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = None
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_18(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = None
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_19(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(None)
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_20(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=None))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_21(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = None

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_22(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(None)

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_23(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=None))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_24(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start < dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO

    def xǁUSTimeZoneǁdst__mutmut_25(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if 2006 < dt.year:
            dststart, dstend = DSTSTART_2007, DSTEND_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = DSTSTART_1987_2006, DSTEND_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = DSTSTART_1967_1986, DSTEND_1967_1986
        else:
            return ZERO

        start = _first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = _first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone
        # from dt first.
        if start <= dt.replace(tzinfo=None) <= end:
            return HOUR
        else:
            return ZERO
    
    xǁUSTimeZoneǁdst__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁUSTimeZoneǁdst__mutmut_1': xǁUSTimeZoneǁdst__mutmut_1, 
        'xǁUSTimeZoneǁdst__mutmut_2': xǁUSTimeZoneǁdst__mutmut_2, 
        'xǁUSTimeZoneǁdst__mutmut_3': xǁUSTimeZoneǁdst__mutmut_3, 
        'xǁUSTimeZoneǁdst__mutmut_4': xǁUSTimeZoneǁdst__mutmut_4, 
        'xǁUSTimeZoneǁdst__mutmut_5': xǁUSTimeZoneǁdst__mutmut_5, 
        'xǁUSTimeZoneǁdst__mutmut_6': xǁUSTimeZoneǁdst__mutmut_6, 
        'xǁUSTimeZoneǁdst__mutmut_7': xǁUSTimeZoneǁdst__mutmut_7, 
        'xǁUSTimeZoneǁdst__mutmut_8': xǁUSTimeZoneǁdst__mutmut_8, 
        'xǁUSTimeZoneǁdst__mutmut_9': xǁUSTimeZoneǁdst__mutmut_9, 
        'xǁUSTimeZoneǁdst__mutmut_10': xǁUSTimeZoneǁdst__mutmut_10, 
        'xǁUSTimeZoneǁdst__mutmut_11': xǁUSTimeZoneǁdst__mutmut_11, 
        'xǁUSTimeZoneǁdst__mutmut_12': xǁUSTimeZoneǁdst__mutmut_12, 
        'xǁUSTimeZoneǁdst__mutmut_13': xǁUSTimeZoneǁdst__mutmut_13, 
        'xǁUSTimeZoneǁdst__mutmut_14': xǁUSTimeZoneǁdst__mutmut_14, 
        'xǁUSTimeZoneǁdst__mutmut_15': xǁUSTimeZoneǁdst__mutmut_15, 
        'xǁUSTimeZoneǁdst__mutmut_16': xǁUSTimeZoneǁdst__mutmut_16, 
        'xǁUSTimeZoneǁdst__mutmut_17': xǁUSTimeZoneǁdst__mutmut_17, 
        'xǁUSTimeZoneǁdst__mutmut_18': xǁUSTimeZoneǁdst__mutmut_18, 
        'xǁUSTimeZoneǁdst__mutmut_19': xǁUSTimeZoneǁdst__mutmut_19, 
        'xǁUSTimeZoneǁdst__mutmut_20': xǁUSTimeZoneǁdst__mutmut_20, 
        'xǁUSTimeZoneǁdst__mutmut_21': xǁUSTimeZoneǁdst__mutmut_21, 
        'xǁUSTimeZoneǁdst__mutmut_22': xǁUSTimeZoneǁdst__mutmut_22, 
        'xǁUSTimeZoneǁdst__mutmut_23': xǁUSTimeZoneǁdst__mutmut_23, 
        'xǁUSTimeZoneǁdst__mutmut_24': xǁUSTimeZoneǁdst__mutmut_24, 
        'xǁUSTimeZoneǁdst__mutmut_25': xǁUSTimeZoneǁdst__mutmut_25
    }
    
    def dst(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁUSTimeZoneǁdst__mutmut_orig"), object.__getattribute__(self, "xǁUSTimeZoneǁdst__mutmut_mutants"), args, kwargs, self)
        return result 
    
    dst.__signature__ = _mutmut_signature(xǁUSTimeZoneǁdst__mutmut_orig)
    xǁUSTimeZoneǁdst__mutmut_orig.__name__ = 'xǁUSTimeZoneǁdst'


Eastern = USTimeZone(-5, "Eastern",  "EST", "EDT")
Central = USTimeZone(-6, "Central",  "CST", "CDT")
Mountain = USTimeZone(-7, "Mountain", "MST", "MDT")
Pacific = USTimeZone(-8, "Pacific",  "PST", "PDT")
