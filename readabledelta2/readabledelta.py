"""
Readabledelta.

Taken and modified from
https://github.com/wimglenn/readabledelta/blob/master/readabledelta.py
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import overload

from dateutil.relativedelta import relativedelta

UTC = timezone.utc


class ExtendedEnum(Enum):
    @classmethod
    def values(cls) -> tuple:  # pragma: no cover
        """Return values of enum"""
        return tuple(c.value for c in cls)


class Style(str, ExtendedEnum):
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


class TDUnit(str, ExtendedEnum):
    YEARS = YEARS
    WEEKS = WEEKS
    DAYS = DAYS
    HOURS = HOURS
    MINUTES = MINUTES
    SECONDS = SECONDS
    MILLISECONDS = MILLISECONDS
    MICROSECONDS = MICROSECONDS


# months are included here because relativedelta knows how to handle it.
class RDUnit(str, ExtendedEnum):
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


@overload
def find_smallest_unit(units: tuple[RDUnit, ...]) -> RDUnit: ...
@overload
def find_smallest_unit(units: tuple[TDUnit, ...]) -> TDUnit: ...
@overload
def find_smallest_unit(units: tuple[str, ...]) -> str: ...
def find_smallest_unit(
    units: tuple[RDUnit | TDUnit | str, ...]
) -> str | RDUnit | TDUnit:
    """Finds the smallest unit in the tuple"""

    def rtn(utype: str) -> RDUnit | TDUnit | str:
        for unit in units:
            if unit == utype:
                return unit

        raise RuntimeError  # pragma: nocover

    if not set(units).issubset(
        (
            YEARS,
            MONTHS,
            WEEKS,
            DAYS,
            HOURS,
            MINUTES,
            SECONDS,
            MILLISECONDS,
            MICROSECONDS,
        )
    ):
        msg = "Unknown units"
        raise ValueError(msg)

    if MICROSECONDS in units:
        return rtn(MICROSECONDS)
    if MILLISECONDS in units:
        return rtn(MILLISECONDS)
    if SECONDS in units:
        return rtn(SECONDS)
    if MINUTES in units:
        return rtn(MINUTES)
    if HOURS in units:
        return rtn(HOURS)
    if DAYS in units:
        return rtn(DAYS)
    if WEEKS in units:
        return rtn(WEEKS)
    if MONTHS in units:
        return rtn(MONTHS)
    if YEARS in units:
        return rtn(YEARS)

    raise RuntimeWarning  # pragma: nocover


@overload
def sort_units(units: tuple[RDUnit, ...]) -> tuple[RDUnit, ...]: ...
@overload
def sort_units(units: tuple[TDUnit, ...]) -> tuple[TDUnit, ...]: ...
@overload
def sort_units(units: tuple[str, ...]) -> tuple[str, ...]: ...
def sort_units(
    units: tuple[RDUnit | TDUnit | str, ...]
) -> tuple[RDUnit | TDUnit | str, ...]:
    """Return tuple of units sorted from largest to smallest time unit"""
    units = tuple(set(units))
    if not set(units).issubset(
        (
            YEARS,
            MONTHS,
            WEEKS,
            DAYS,
            HOURS,
            MINUTES,
            SECONDS,
            MILLISECONDS,
            MICROSECONDS,
        )
    ):
        msg = "Unknown units"
        raise ValueError(msg)

    new_units = []

    def append(utype: str) -> None:
        for unit in units:
            if unit == utype:
                new_units.append(unit)

    if YEARS in units:
        append(YEARS)
    if MONTHS in units:
        append(MONTHS)
    if WEEKS in units:
        append(WEEKS)
    if DAYS in units:
        append(DAYS)
    if HOURS in units:
        append(HOURS)
    if MINUTES in units:
        append(MINUTES)
    if SECONDS in units:
        append(SECONDS)
    if MILLISECONDS in units:
        append(MILLISECONDS)
    if MICROSECONDS in units:
        append(MICROSECONDS)
    return tuple(new_units)


################################################################################
def split_timedelta_units(
    delta: timedelta, units: tuple[TDUnit | str, ...] = tuple(TDUnit)
) -> dict[TDUnit, int]:
    """

    :param timedelta delta:
    :param units: array of time magnitudes to be used for output
    """
    units = sort_units(units)
    if not set(units).issubset(tuple(TDUnit)):
        msg = f"units can only be the following: {tuple(TDUnit)}"
        raise ValueError(msg)

    delta = abs(delta)

    # timedeltas are normalised to just days, seconds, microseconds in cpython
    data = {}
    days = delta.days
    seconds = delta.seconds
    microseconds = delta.microseconds

    units_list = list(units)

    def have_leftovers() -> bool:
        return bool(days or seconds or microseconds)

    if TDUnit.YEARS in units_list:
        data[TDUnit.YEARS], days = divmod(days, 365)
        units_list.pop(0)
    else:
        data[TDUnit.YEARS] = 0

    if not units_list and have_leftovers():
        weeks, _ = divmod(days, 7)
        if weeks:
            units_list.append(TDUnit.WEEKS)

    if TDUnit.WEEKS in units_list:
        data[TDUnit.WEEKS], days = divmod(days, 7)
        units_list.pop(0)
    else:
        data[TDUnit.WEEKS] = 0

    if not units_list and have_leftovers() and days:
        units_list.append(TDUnit.DAYS)

    if TDUnit.DAYS in units_list:
        data[TDUnit.DAYS] = days
        units_list.pop(0)
    else:
        data[TDUnit.DAYS] = 0
        seconds += days * 86400  # 24 * 60 * 60

    if not units_list and have_leftovers():
        hours, _ = divmod(seconds, 60 * 60)
        if hours:
            units_list.append(TDUnit.HOURS)

    if TDUnit.HOURS in units_list:
        data[TDUnit.HOURS], seconds = divmod(seconds, 60 * 60)
        units_list.pop(0)
    else:
        data[TDUnit.HOURS] = 0

    if not units_list and have_leftovers():
        minutes, _ = divmod(seconds, 60)
        if minutes:
            units_list.append(TDUnit.MINUTES)

    if TDUnit.MINUTES in units_list:
        data[TDUnit.MINUTES], seconds = divmod(seconds, 60)
        units_list.pop(0)
    else:
        data[TDUnit.MINUTES] = 0

    if not units_list and have_leftovers() and seconds:
        units_list.append(TDUnit.SECONDS)

    if TDUnit.SECONDS in units_list:
        data[TDUnit.SECONDS] = seconds
        units_list.pop(0)
    else:
        data[TDUnit.SECONDS] = 0
        microseconds += seconds * 1000000  # 1000 * 1000

    if not units_list and have_leftovers():
        milliseconds, _ = divmod(microseconds, 1000)
        if milliseconds:
            units_list.append(TDUnit.MILLISECONDS)

    if TDUnit.MILLISECONDS in units_list:
        data[TDUnit.MILLISECONDS], microseconds = divmod(microseconds, 1000)
        units_list.pop(0)
    else:
        data[TDUnit.MILLISECONDS] = 0

    if not units_list and have_leftovers() and microseconds:
        units_list.append(TDUnit.MICROSECONDS)

    if TDUnit.MICROSECONDS in units_list:
        data[TDUnit.MICROSECONDS] = microseconds
        units_list.pop(0)
    else:
        data[TDUnit.MICROSECONDS] = 0

    return data


################################################################################
def split_relativedelta_units(
    delta: relativedelta, units: tuple[RDUnit | str, ...] = tuple(RDUnit)
) -> dict[RDUnit, int]:
    """

    :param relativedelta delta:
    :param units: array of time magnitudes to be used for output
    """
    units = sort_units(units)
    if not set(units).issubset(tuple(RDUnit)):
        msg = f"units can only be the following: {tuple(RDUnit)}"
        raise ValueError(msg)

    delta = abs(delta)

    data = {}
    years = delta.years
    months = delta.months
    weeks = delta.weeks
    days = delta.days
    hours = delta.hours
    minutes = delta.minutes
    seconds = delta.seconds
    microseconds = delta.microseconds

    units_list = list(units)

    def have_leftovers() -> bool:
        return bool(weeks or days or hours or minutes or seconds or microseconds)

    # years are relative due to leapyear.... so unless they are in the delta..
    # we won't calculate them
    if RDUnit.YEARS in units_list:
        data[RDUnit.YEARS] = years
        units_list.pop(0)
    else:
        data[RDUnit.YEARS] = 0
        months += years * 12

    # it's impossible to filter out months because there is no way to
    # convert them to smaller units without the relative dates.
    if RDUnit.MONTHS not in units_list and months:
        units_list.append(RDUnit.MONTHS)
        units_list = list(sort_units(tuple(units_list)))

    if RDUnit.MONTHS in units_list:
        data[RDUnit.MONTHS] = months
        months = 0
        units_list.pop(0)
    else:
        data[RDUnit.MONTHS] = 0

    if not units_list and have_leftovers():
        weeks, _ = divmod(days, 7)
        if weeks:
            units_list.append(RDUnit.WEEKS)

    if RDUnit.WEEKS in units_list:
        data[RDUnit.WEEKS], days = divmod(days, 7)
        weeks = 0
        units_list.pop(0)
    else:
        data[RDUnit.WEEKS] = 0

    if not units_list and have_leftovers() and days:
        units_list.append(RDUnit.DAYS)

    if RDUnit.DAYS in units_list:
        data[RDUnit.DAYS] = days
        days = 0
        units_list.pop(0)
    else:
        data[RDUnit.DAYS] = 0
        hours += days * 24

    if not units_list and have_leftovers() and hours:
        units_list.append(RDUnit.HOURS)

    if RDUnit.HOURS in units_list:
        data[RDUnit.HOURS] = hours
        hours = 0
        units_list.pop(0)
    else:
        data[RDUnit.HOURS] = 0
        minutes += hours * 60

    if not units_list and have_leftovers() and minutes:
        units_list.append(RDUnit.MINUTES)

    if RDUnit.MINUTES in units_list:
        data[RDUnit.MINUTES] = minutes
        minutes = 0
        units_list.pop(0)
    else:
        data[RDUnit.MINUTES] = 0
        seconds += minutes * 60

    if not units_list and have_leftovers() and seconds:
        units_list.append(RDUnit.SECONDS)

    if RDUnit.SECONDS in units_list:
        data[RDUnit.SECONDS] = seconds
        seconds = 0
        units_list.pop(0)
    else:
        data[RDUnit.SECONDS] = 0
        microseconds += seconds * 1000000  # 1000 * 1000

    if not units_list and have_leftovers() and microseconds:
        units_list.append(RDUnit.MICROSECONDS)

    if RDUnit.MICROSECONDS in units_list:
        data[RDUnit.MICROSECONDS] = microseconds
        units_list.pop(0)
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
    style: Style,
    units: tuple[RDUnit | TDUnit | str, ...],
    showzero: bool,  # noqa: FBT001
    sign: str,
) -> str:
    output = []
    for k, val in data.items():
        if not val and k not in units:
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

    if len(output) == 0:  # pragma: nocover
        raise RuntimeError
    if len(output) == 1:
        result = output[0]
    else:
        left, right = output[:-1], output[-1:]
        result = f"{', '.join(left)} and {right[0]}"

    return result


################################################################################
def from_timedelta(
    delta: timedelta,
    style: Style = Style.NORMAL,
    units: tuple[TDUnit | str, ...] | None = None,
    *,
    include_sign: bool = True,
    showzero: bool = False,
) -> str:
    """
    Create Human readable timedelta string.

    :param timedelta delta:
    :param style: normal, short, abbrev
    :param units: tuple of timeunits to be used for output
    :param include_sign: false will prevent sign from appearing
            allows you to create negative deltas but still have a human sentence like
            '2 hours ago' instead of '-2 hours ago'
    :param bool showzero: prints out the values even if they are zero
    """
    negative = is_negative_timedelta(delta)
    sign = "-" if include_sign and negative else ""
    delta = abs(delta)

    if units is None or len(units) == 0:
        units = tuple(TDUnit)
    else:
        units = tuple(set(units))
        if not set(units).issubset(tuple(TDUnit)):
            msg = f"units can only be the following: {tuple(TDUnit)}"
            raise ValueError(msg)

    data = split_timedelta_units(delta, units)

    if not delta and not showzero:
        showzero = True
        units = (TDUnit.SECONDS,)

    return _process_output(data, style, units, showzero, sign)


################################################################################
def from_relativedelta(
    delta: relativedelta,
    style: Style = Style.NORMAL,
    units: tuple[RDUnit | str, ...] | None = None,
    *,
    include_sign: bool = True,
    showzero: bool = False,
) -> str:
    """
    Create Human readable relativedelta string.

    :param relativedelta delta:
    :param style: 0: normal names, 1: short names, 2: abbreviations
    :param units: tuple of timeunits to be used for output
    :param include_sign: false will prevent sign from appearing
            allows you to create negative deltas but still have a human sentence like
            '2 hours ago' instead of '-2 hours ago'
    :param bool showzero: prints out the values even if they are zero
    """
    negative = is_negative_relativedelta(delta)
    sign = "-" if include_sign and negative else ""
    delta = abs(delta)

    if units is None or len(units) == 0:
        units = tuple(RDUnit)
    else:
        units = tuple(set(units))
        if not set(units).issubset(tuple(RDUnit)):
            msg = f"units can only be the following: {tuple(RDUnit)}"
            raise ValueError(msg)

    data = split_relativedelta_units(delta, units)

    if not delta and not showzero:
        showzero = True
        units = (RDUnit.SECONDS,)

    return _process_output(data, style, units, showzero, sign)


################################################################################
def extract_units(
    delta: timedelta, units: tuple[TDUnit, ...] = tuple(TDUnit)
) -> tuple[TDUnit, ...]:
    """Given a timedelta, determine all the time magnitudes within said delta."""
    units = tuple(set(units))
    if not set(units).issubset(tuple(TDUnit)):
        msg = f"units can only be the following: {tuple(TDUnit)}"
        raise ValueError(msg)
    data = split_timedelta_units(delta, units)
    runits = []
    for key, val in data.items():
        if key not in units:
            continue

        if val:
            runits.append(key)
    return tuple(runits)
