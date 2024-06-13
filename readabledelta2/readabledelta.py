"""
Readabledelta.

Taken and modified from
https://github.com/wimglenn/readabledelta/blob/master/readabledelta.py
"""

from __future__ import annotations

import warnings
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, TypeVar

from dateutil.relativedelta import relativedelta

if TYPE_CHECKING:
    from collections.abc import Sequence

UTC = timezone.utc

NORMAL = 0
SHORT = 1
ABBREV = 2

YEARS = "years"
MONTHS = "months"
WEEKS = "weeks"
DAYS = "days"
HOURS = "hours"
MINUTES = "minutes"
SECONDS = "seconds"
MILLISECONDS = "milliseconds"
MICROSECONDS = "microseconds"


T_tunits = dict[str, dict[str, str]]
T_delta = relativedelta | timedelta

# @formatter:off
# fmt: off
TIME_UNITS: T_tunits = {
    MICROSECONDS: {"plural": "microseconds", "singular": "microsecond", "abbrev": "µs", "short": "µsecs"},  # noqa: E501
    MILLISECONDS: {"plural": "milliseconds", "singular": "millisecond", "abbrev": "ms", "short": "msecs"},  # noqa: E501
    SECONDS     : {"plural": "seconds",      "singular": "second",      "abbrev": "s",  "short": "secs"},  # noqa: E501
    MINUTES     : {"plural": "minutes",      "singular": "minute",      "abbrev": "m",  "short": "mins"},  # noqa: E501
    HOURS       : {"plural": "hours",        "singular": "hour",        "abbrev": "h",  "short": "hrs"},  # noqa: E501
    DAYS        : {"plural": "days",         "singular": "day",         "abbrev": "D",  "short": "days"},  # noqa: E501
    WEEKS       : {"plural": "weeks",        "singular": "week",        "abbrev": "W",  "short": "wks"},  # noqa: E501
    MONTHS      : {"plural": "months",       "singular": "month",       "abbrev": "M",  "short": "mnths"},  # noqa: E501
    YEARS       : {"plural": "years",        "singular": "year",        "abbrev": "Y",  "short": "yrs"},  # noqa: E501
            }
# fmt: on
# @formatter:on


TIMEDELTA_ALLOWED_KEYS = (
    YEARS,
    WEEKS,
    DAYS,
    HOURS,
    MINUTES,
    SECONDS,
    MILLISECONDS,
    MICROSECONDS,
)
# months are included here because relativedelta knows how to handle it.
RELATIVEDELTA_ALLOWED_KEYS = (
    YEARS,
    MONTHS,
    WEEKS,
    DAYS,
    HOURS,
    MINUTES,
    SECONDS,
    MICROSECONDS,
)


class ReadableDelta(timedelta):
    """Human readable version of timedelta."""

    def __new__(cls: type[T], *args: Any, **kwargs: Any) -> T:  # noqa: ANN401
        """Creates a timedelta"""
        years = kwargs.pop(YEARS, 0)
        if DAYS in kwargs:
            kwargs[DAYS] += 365 * years
        elif years:
            arg0 = args[0] if args else 0
            args = (365 * years + arg0,) + args[1:]
        return timedelta.__new__(cls, *args, **kwargs)

    @classmethod
    def from_timedelta(cls: type[T], dt: timedelta) -> T:
        """Converts timedelta to readabledelta."""
        return cls(days=dt.days, seconds=dt.seconds, microseconds=dt.microseconds)

    def __unicode__(self) -> str:
        return to_string(self)

    __str__ = __unicode__


T = TypeVar("T", bound=ReadableDelta)


################################################################################
def split_timedelta_units(
    delta: timedelta, keys: Sequence[str] | None = None
) -> dict[str, int]:
    """

    :param timedelta delta:
    :param keys: array of time magnitudes to be used for output
    :return:
    """
    if keys is None:
        keys = TIMEDELTA_ALLOWED_KEYS

    delta = abs(delta)

    # timedeltas are normalised to just days, seconds, microseconds in cpython
    data = {}
    days = delta.days
    seconds = delta.seconds
    microseconds = delta.microseconds

    if YEARS in keys:
        data[YEARS], days = divmod(days, 365)
    else:
        data[YEARS] = 0

    if WEEKS in keys:
        data[WEEKS], days = divmod(days, 7)
    else:
        data[WEEKS] = 0

    if DAYS in keys:
        data[DAYS] = days
    else:
        data[DAYS] = 0
        seconds += days * 86400  # 24 * 60 * 60

    if HOURS in keys:
        data[HOURS], seconds = divmod(seconds, 60 * 60)
    else:
        data[HOURS] = 0

    if MINUTES in keys:
        data[MINUTES], seconds = divmod(seconds, 60)
    else:
        data[MINUTES] = 0

    if SECONDS in keys:
        data[SECONDS] = seconds
    else:
        data[SECONDS] = 0
        microseconds += seconds * 1000000  # 1000 * 1000

    if MILLISECONDS in keys:
        data[MILLISECONDS], microseconds = divmod(microseconds, 1000)
    else:
        data[MILLISECONDS] = 0

    if MICROSECONDS in keys:
        data[MICROSECONDS] = microseconds
    else:
        data[MICROSECONDS] = 0

    return data


################################################################################
def split_relativedelta_units(
    delta: relativedelta, keys: Sequence[str] | None = None
) -> dict[str, int]:
    """

    :param delta:
    :param keys: array of time magnitudes to be used for output
    :return:
    """
    if keys is None:
        keys = RELATIVEDELTA_ALLOWED_KEYS
    else:
        assert set(keys).issubset(
            RELATIVEDELTA_ALLOWED_KEYS
        ), f"keys can only be {RELATIVEDELTA_ALLOWED_KEYS}"

    delta = abs(delta)

    # timedeltas are normalised to just days, seconds, microseconds in cpython
    data = {}
    years = delta.years
    months = delta.months
    days = delta.days
    hours = delta.hours
    minutes = delta.minutes
    seconds = delta.seconds
    microseconds = delta.microseconds

    # years are relative due to leapyear.... so unless they are in the delta..
    # we won't calculate them
    if YEARS in keys:
        data[YEARS] = years
    else:
        data[YEARS] = 0
        months += years * 12

    # it's impossible to filter out months because there is no way to
    # convert them to smaller units without the relative dates.
    if MONTHS not in keys and months:
        warnings.warn(
            "Cannot reduce months down to smaller units", Warning, stacklevel=1
        )

    data[MONTHS] = months

    if WEEKS in keys:
        data[WEEKS], days = divmod(days, 7)
    else:
        data[WEEKS] = 0

    if DAYS in keys:
        data[DAYS] = days
    else:
        data[DAYS] = 0
        hours += days * 24

    if HOURS in keys:
        data[HOURS] = hours
    else:
        data[HOURS] = 0
        minutes += hours * 60

    if MINUTES in keys:
        data[MINUTES] = minutes
    else:
        data[MINUTES] = 0
        seconds += minutes * 60

    if SECONDS in keys:
        data[SECONDS] = seconds
    else:
        data[SECONDS] = 0
        microseconds += seconds * 1000000  # 1000 * 1000

    if MICROSECONDS in keys:
        data[MICROSECONDS] = microseconds
    else:
        data[MICROSECONDS] = 0

    return data


def is_negative_relativedelta(
    delta: T_delta, dt: datetime = datetime(1970, 1, 1, tzinfo=UTC)
) -> bool:
    """Determine if relative delta is negative"""
    return (dt + delta) < (dt + relativedelta())


################################################################################
def to_string(
    delta: timedelta,
    short: int = NORMAL,
    keys: Sequence[str] | None = None,
    *,
    include_sign: bool = True,
    showzero: bool = False,
) -> str:
    """
    Create Human readable timedelta string.

    :param timedelta | ReadableDelta delta:
    :param short: 1: uses short names, 2: uses abbreviation names
    :param include_sign: false will prevent sign from appearing
            allows you to create negative deltas but still have a human sentence like
            '2 hours ago' instead of '-2 hours ago'
    :param keys: array of timeunits to be used for output
    :param bool showzero: prints out the values even if they are zero
    :return:
    :rtype: str
    """
    negative = delta < timedelta(0)
    sign = "-" if include_sign and negative else ""
    delta = abs(delta)

    if keys is None:
        keys = TIMEDELTA_ALLOWED_KEYS
    else:
        assert set(keys).issubset(
            TIMEDELTA_ALLOWED_KEYS
        ), f"keys can only be {TIMEDELTA_ALLOWED_KEYS}"

    data = split_timedelta_units(delta, keys)

    output = []
    for k in keys:
        val = data[k]
        if val == 0 and showzero is False:
            continue
        singular = val == 1
        tu = TIME_UNITS.get(k)
        if tu is None:
            msg = f"Invalid key {k}"
            raise ValueError(msg)

        if short == NORMAL:
            unit = tu.get("plural")
        elif short == SHORT:
            unit = tu.get("short")
        elif short == ABBREV:
            unit = tu.get("abbrev")
        else:
            msg = f"Invalid argument {short}"
            raise ValueError(msg)
        if unit is None:
            msg = f"Invalid argument {short}"
            raise ValueError(msg)

        # make magnitude singular
        if short in [NORMAL, SHORT] and singular:
            unit = unit[:-1]

        output.append(f"{sign}{val} {unit}")
        # we only need to show the negative sign once.
        if val != 0:
            sign = ""

    if not output:
        result = str(delta)
    elif len(output) == 1:
        result = output[0]
    else:
        left, right = output[:-1], output[-1:]
        result = f"{', '.join(left)} and {right[0]}"

    return result


################################################################################
def extract_units(delta: timedelta, keys: Sequence[str] | None = None) -> list[str]:
    """
    Given a timedelta, determine all the time magnitudes within said delta.

    :param timedelta delta:
    :return:
    """
    if keys is None:
        keys = TIMEDELTA_ALLOWED_KEYS
    data = split_timedelta_units(delta, keys)
    rkeys = []
    for key in keys:
        if data[key]:
            rkeys.append(key)
    return rkeys


################################################################################
def from_relativedelta(
    rdelta: relativedelta,
    short: int = NORMAL,
    keys: Sequence[str] | None = None,
    *,
    include_sign: bool = True,
    showzero: bool = False,
) -> str:
    """
    Create Human readable relativedelta string.

    :param ReadableDelta rdelta:
    :param short: 1: uses short names, 2: uses abbreviation names
    :param include_sign: false will prevent sign from appearing
            allows you to create negative deltas but still have a human sentence like
            '2 hours ago' instead of '-2 hours ago'
    :param keys: array of timeunits to be used for output
    :param bool showzero: prints out the values even if they are zero
    :return:
    :rtype: str
    """
    negative = is_negative_relativedelta(rdelta)
    sign = "-" if include_sign and negative else ""
    rdelta = abs(rdelta)

    if keys is None:
        keys = RELATIVEDELTA_ALLOWED_KEYS
    else:
        assert set(keys).issubset(
            RELATIVEDELTA_ALLOWED_KEYS
        ), f"keys can only be {RELATIVEDELTA_ALLOWED_KEYS}"

    data = split_relativedelta_units(rdelta, keys)

    output = []
    for k in keys:
        val = data[k]
        if val == 0 and showzero is False:
            continue
        singular = val == 1
        tu = TIME_UNITS.get(k)
        if tu is None:
            msg = f"Invalid key {k}"
            raise ValueError(msg)

        if short == NORMAL:
            unit = tu.get("plural")
        elif short == SHORT:
            unit = tu.get("short")
        elif short == ABBREV:
            unit = tu.get("abbrev")
        else:
            msg = f"Invalid argument {short}"
            raise ValueError(msg)
        if unit is None:
            msg = f"Invalid argument {short}"
            raise ValueError(msg)

        # make unit singular if needed
        if short in [NORMAL, SHORT] and singular:
            unit = unit[:-1]

        output.append(f"{sign}{val} {unit}")
        # we only need to show the negative sign once.
        if val != 0:
            sign = ""

    if not output:
        result = "now"
    elif len(output) == 1:
        result = output[0]
    else:
        left, right = output[:-1], output[-1:]
        result = f"{', '.join(left)} and {right[0]}"

    return result
