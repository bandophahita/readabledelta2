"""
Readabledelta.

Taken and modified from
https://github.com/wimglenn/readabledelta/blob/master/readabledelta.py
"""

from __future__ import annotations

import warnings
from datetime import datetime, timedelta, timezone
from enum import Enum, StrEnum

from dateutil.relativedelta import relativedelta

UTC = timezone.utc


class ExtendedEnum(Enum):
    @classmethod
    def values(cls) -> tuple:  # pragma: no cover
        """Return values of enum"""
        return tuple(c.value for c in cls)


class Style(StrEnum, ExtendedEnum):
    NORMAL = "normal"
    SHORT = "short"
    ABBREV = "abbrev"


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


T_delta = relativedelta | timedelta

# @formatter:off
# fmt: off
TIME_UNITS: dict[str, dict[Style, str]] = {
    MICROSECONDS: {Style.NORMAL: "microseconds", Style.SHORT: "µsecs", Style.ABBREV: "µs"},
    MILLISECONDS: {Style.NORMAL: "milliseconds", Style.SHORT: "msecs", Style.ABBREV: "ms"},
    SECONDS     : {Style.NORMAL: "seconds",      Style.SHORT: "secs",  Style.ABBREV: "s"},
    MINUTES     : {Style.NORMAL: "minutes",      Style.SHORT: "mins",  Style.ABBREV: "m"},
    HOURS       : {Style.NORMAL: "hours",        Style.SHORT: "hrs",   Style.ABBREV: "h"},
    DAYS        : {Style.NORMAL: "days",         Style.SHORT: "days",  Style.ABBREV: "D"},
    WEEKS       : {Style.NORMAL: "weeks",        Style.SHORT: "wks",   Style.ABBREV: "W"},
    MONTHS      : {Style.NORMAL: "months",       Style.SHORT: "mnths", Style.ABBREV: "M"},
    YEARS       : {Style.NORMAL: "years",        Style.SHORT: "yrs",   Style.ABBREV: "Y"},
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
    """
    keys = tuple(set(keys))
    if not set(keys).issubset(tuple(TDUnit)):
        msg = f"keys can only be the following: {tuple(TDUnit)}"
        raise ValueError(msg)

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

    :param relativedelta delta:
    :param keys: array of time magnitudes to be used for output
    """
    keys = tuple(set(keys))
    if not set(keys).issubset(tuple(RDUnit)):
        msg = f"keys can only be the following: {tuple(RDUnit)}"
        raise ValueError(msg)

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


def is_negative_relativedelta(delta: relativedelta) -> bool:
    """Determine if relativedelta is negative"""
    dt: datetime = datetime(1970, 1, 1, tzinfo=UTC)
    return (dt + delta) < (dt + relativedelta())


def is_negative_timedelta(delta: timedelta) -> bool:
    """Determine if timedelta is negative"""
    return delta < timedelta(0)


def _process_output(
    data: dict[RDUnit, int] | dict[TDUnit, int],
    keys: tuple[RDUnit | TDUnit | str, ...],
    showzero: bool,
    style: Style,
    sign: str,
) -> str:
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

        unit = tu.get(style)
        if unit is None:
            msg = f"Invalid argument {style}"
            raise ValueError(msg)

        # make magnitude singular
        if style in [Style.NORMAL, Style.SHORT] and singular:
            unit = unit[:-1]

        output.append(f"{sign}{val} {unit}")
        # we only need to show the negative sign once.
        if val != 0:
            sign = ""

    if len(output) == 0:
        result = "0:00:00"
    elif len(output) == 1:
        result = output[0]
    else:
        left, right = output[:-1], output[-1:]
        result = f"{', '.join(left)} and {right[0]}"

    return result


################################################################################
def from_timedelta(
    delta: timedelta,
    style: Style = Style.NORMAL,
    keys: tuple[TDUnit | str, ...] | None = None,
    *,
    include_sign: bool = True,
    showzero: bool = False,
) -> str:
    """
    Create Human readable timedelta string.

    :param timedelta delta:
    :param style: normal, short, abbrev
    :param keys: tuple of timeunits to be used for output
    :param include_sign: false will prevent sign from appearing
            allows you to create negative deltas but still have a human sentence like
            '2 hours ago' instead of '-2 hours ago'
    :param bool showzero: prints out the values even if they are zero
    """
    negative = is_negative_timedelta(delta)
    sign = "-" if include_sign and negative else ""
    delta = abs(delta)

    if keys is None:
        keys = tuple(TDUnit)
    else:
        keys = tuple(set(keys))
        if not set(keys).issubset(tuple(TDUnit)):
            msg = f"keys can only be the following: {tuple(TDUnit)}"
            raise ValueError(msg)

    data = split_timedelta_units(delta, keys)

    return _process_output(data, keys, showzero, style, sign)


################################################################################
def extract_units(
    delta: timedelta, keys: tuple[TDUnit, ...] = tuple(TDUnit)
) -> tuple[TDUnit, ...]:
    """Given a timedelta, determine all the time magnitudes within said delta."""
    keys = tuple(set(keys))
    if not set(keys).issubset(tuple(TDUnit)):
        msg = f"keys can only be the following: {tuple(TDUnit)}"
        raise ValueError(msg)
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

    :param relativedelta rdelta:
    :param style: 0: normal names, 1: short names, 2: abbreviations
    :param keys: tuple of timeunits to be used for output
    :param include_sign: false will prevent sign from appearing
            allows you to create negative deltas but still have a human sentence like
            '2 hours ago' instead of '-2 hours ago'
    :param bool showzero: prints out the values even if they are zero
    """
    negative = is_negative_relativedelta(rdelta)
    sign = "-" if include_sign and negative else ""
    rdelta = abs(rdelta)

    if keys is None:
        keys = tuple(RDUnit)
    else:
        keys = tuple(set(keys))
        if not set(keys).issubset(tuple(RDUnit)):
            msg = f"keys can only be the following: {tuple(RDUnit)}"
            raise ValueError(msg)

    data = split_relativedelta_units(rdelta, keys)

    return _process_output(data, keys, showzero, style, sign)
