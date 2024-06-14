"""
Readabledelta.

Taken and modified from
https://github.com/wimglenn/readabledelta/blob/master/readabledelta.py
"""

from __future__ import annotations

import warnings
from datetime import datetime, timedelta, timezone
from enum import Enum, IntEnum, StrEnum
from typing import TypedDict

from dateutil.relativedelta import relativedelta

UTC = timezone.utc


class ExtendedEnum(Enum):
    @classmethod
    def values(cls) -> tuple:  # pragma: no cover
        """Return values of enum"""
        return tuple(c.value for c in cls)


class Style(IntEnum, ExtendedEnum):
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


class TDUnit(StrEnum, ExtendedEnum):
    YEARS = YEARS
    WEEKS = WEEKS
    DAYS = DAYS
    HOURS = HOURS
    MINUTES = MINUTES
    SECONDS = SECONDS
    MILLISECONDS = MILLISECONDS
    MICROSECONDS = MICROSECONDS


# months are included here because relativedelta knows how to handle it.
class RDUnit(StrEnum, ExtendedEnum):
    YEARS = YEARS
    MONTHS = MONTHS
    WEEKS = WEEKS
    DAYS = DAYS
    HOURS = HOURS
    MINUTES = MINUTES
    SECONDS = SECONDS
    MICROSECONDS = MICROSECONDS


class UnitTranslation(TypedDict):
    plural: str
    singular: str
    abbrev: str
    short: str


T_delta = relativedelta | timedelta

# @formatter:off
# fmt: off
TIME_UNITS: dict[str, UnitTranslation] = {
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


################################################################################
def split_timedelta_units(
    delta: timedelta, keys: tuple[TDUnit | str, ...] = tuple(TDUnit)
) -> dict[TDUnit, int]:
    """

    :param timedelta delta:
    :param keys: array of time magnitudes to be used for output
    :return:
    """
    keys = tuple(set(keys))
    assert set(keys).issubset(tuple(TDUnit)), f"keys can only be {tuple(TDUnit)}"

    delta = abs(delta)

    # timedeltas are normalised to just days, seconds, microseconds in cpython
    data = {}
    days = delta.days
    seconds = delta.seconds
    microseconds = delta.microseconds

    if TDUnit.YEARS in keys:
        data[TDUnit.YEARS], days = divmod(days, 365)
    else:
        data[TDUnit.YEARS] = 0

    if TDUnit.WEEKS in keys:
        data[TDUnit.WEEKS], days = divmod(days, 7)
    else:
        data[TDUnit.WEEKS] = 0

    if TDUnit.DAYS in keys:
        data[TDUnit.DAYS] = days
    else:
        data[TDUnit.DAYS] = 0
        seconds += days * 86400  # 24 * 60 * 60

    if TDUnit.HOURS in keys:
        data[TDUnit.HOURS], seconds = divmod(seconds, 60 * 60)
    else:
        data[TDUnit.HOURS] = 0

    if TDUnit.MINUTES in keys:
        data[TDUnit.MINUTES], seconds = divmod(seconds, 60)
    else:
        data[TDUnit.MINUTES] = 0

    if TDUnit.SECONDS in keys:
        data[TDUnit.SECONDS] = seconds
    else:
        data[TDUnit.SECONDS] = 0
        microseconds += seconds * 1000000  # 1000 * 1000

    if TDUnit.MILLISECONDS in keys:
        data[TDUnit.MILLISECONDS], microseconds = divmod(microseconds, 1000)
    else:
        data[TDUnit.MILLISECONDS] = 0

    if TDUnit.MICROSECONDS in keys:
        data[TDUnit.MICROSECONDS] = microseconds
    else:
        data[TDUnit.MICROSECONDS] = 0

    return data


################################################################################
def split_relativedelta_units(
    delta: relativedelta, keys: tuple[RDUnit | str, ...] = tuple(RDUnit)
) -> dict[RDUnit, int]:
    """

    :param delta:
    :param keys: array of time magnitudes to be used for output
    :return:
    """
    keys = tuple(set(keys))
    assert set(keys).issubset(tuple(RDUnit)), f"keys can only be {tuple(RDUnit)}"

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
    if RDUnit.YEARS in keys:
        data[RDUnit.YEARS] = years
    else:
        data[RDUnit.YEARS] = 0
        months += years * 12

    # it's impossible to filter out months because there is no way to
    # convert them to smaller units without the relative dates.
    if RDUnit.MONTHS not in keys and months:
        warnings.warn(
            "Cannot reduce months down to smaller units", Warning, stacklevel=1
        )

    data[RDUnit.MONTHS] = months

    if RDUnit.WEEKS in keys:
        data[RDUnit.WEEKS], days = divmod(days, 7)
    else:
        data[RDUnit.WEEKS] = 0

    if RDUnit.DAYS in keys:
        data[RDUnit.DAYS] = days
    else:
        data[RDUnit.DAYS] = 0
        hours += days * 24

    if RDUnit.HOURS in keys:
        data[RDUnit.HOURS] = hours
    else:
        data[RDUnit.HOURS] = 0
        minutes += hours * 60

    if RDUnit.MINUTES in keys:
        data[RDUnit.MINUTES] = minutes
    else:
        data[RDUnit.MINUTES] = 0
        seconds += minutes * 60

    if RDUnit.SECONDS in keys:
        data[RDUnit.SECONDS] = seconds
    else:
        data[RDUnit.SECONDS] = 0
        microseconds += seconds * 1000000  # 1000 * 1000

    if RDUnit.MICROSECONDS in keys:
        data[RDUnit.MICROSECONDS] = microseconds
    else:
        data[RDUnit.MICROSECONDS] = 0

    return data


def is_negative_relativedelta(
    delta: T_delta, dt: datetime = datetime(1970, 1, 1, tzinfo=UTC)
) -> bool:
    """Determine if relative delta is negative"""
    return (dt + delta) < (dt + relativedelta())


################################################################################
def to_string(
    delta: timedelta,
    style: Style = Style.NORMAL,
    keys: tuple[TDUnit | str, ...] | None = None,
    *,
    include_sign: bool = True,
    showzero: bool = False,
) -> str:
    """
    Create Human readable timedelta string.

    :param timedelta | ReadableDelta delta:
    :param style: 1: uses short names, 2: uses abbreviation names
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
        keys = tuple(TDUnit)
    else:
        keys = tuple(set(keys))
        assert set(keys).issubset(tuple(TDUnit)), f"keys can only be {tuple(TDUnit)}"

    data = split_timedelta_units(delta, keys)

    output = []
    for k, val in data.items():
        if k not in keys:
            continue
        if val == 0 and showzero is False:
            continue
        singular = val == 1
        tu = TIME_UNITS.get(k)
        if tu is None:  # pragma: no cover
            msg = f"Invalid key {k}"
            raise ValueError(msg)

        if style == Style.NORMAL:
            unit = tu.get("plural")
        elif style == Style.SHORT:
            unit = tu.get("short")
        elif style == Style.ABBREV:
            unit = tu.get("abbrev")
        else:
            msg = f"Invalid argument {style}"
            raise ValueError(msg)
        if unit is None:  # pragma: no cover
            msg = f"Invalid argument {style}"
            raise ValueError(msg)

        # make magnitude singular
        if style in [Style.NORMAL, Style.SHORT] and singular:
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
def extract_units(
    delta: timedelta, keys: tuple[TDUnit, ...] = tuple(TDUnit)
) -> tuple[TDUnit, ...]:
    """
    Given a timedelta, determine all the time magnitudes within said delta.

    :param timedelta delta:
    :return:
    """
    keys = tuple(set(keys))
    assert set(keys).issubset(tuple(TDUnit)), f"keys can only be {tuple(TDUnit)}"
    data = split_timedelta_units(delta, keys)
    rkeys = []
    for key, val in data.items():
        if key not in keys:
            continue

        if val:
            rkeys.append(key)
    return tuple(rkeys)


################################################################################
def from_relativedelta(
    rdelta: relativedelta,
    style: Style = Style.NORMAL,
    keys: tuple[RDUnit | str, ...] | None = None,
    *,
    include_sign: bool = True,
    showzero: bool = False,
) -> str:
    """
    Create Human readable relativedelta string.

    :param ReadableDelta rdelta:
    :param style: 1: uses short names, 2: uses abbreviation names
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
        keys = tuple(RDUnit)
    else:
        keys = tuple(set(keys))
        assert set(keys).issubset(tuple(RDUnit)), f"keys can only be {tuple(RDUnit)}"

    data = split_relativedelta_units(rdelta, keys)

    output = []
    for k, val in data.items():
        if k not in keys:
            continue
        if val == 0 and showzero is False:
            continue
        singular = val == 1
        tu = TIME_UNITS.get(k)
        if tu is None:  # pragma: no cover
            msg = f"Invalid key {k}"
            raise ValueError(msg)

        if style == Style.NORMAL:
            unit = tu.get("plural")
        elif style == Style.SHORT:
            unit = tu.get("short")
        elif style == Style.ABBREV:
            unit = tu.get("abbrev")
        else:
            msg = f"Invalid argument {style}"
            raise ValueError(msg)
        if unit is None:  # pragma: no cover
            msg = f"Invalid argument {style}"
            raise ValueError(msg)

        # make unit singular if needed
        if style in [Style.NORMAL, Style.SHORT] and singular:
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
