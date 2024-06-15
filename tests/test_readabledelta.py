from __future__ import annotations

import re
from datetime import timedelta
from enum import StrEnum

import pytest
from dateutil.relativedelta import relativedelta

from readabledelta2 import Style, from_relativedelta, from_timedelta
from readabledelta2.readabledelta import (
    DAYS,
    HOURS,
    MICROSECONDS,
    MILLISECONDS,
    MINUTES,
    MONTHS,
    SECONDS,
    WEEKS,
    YEARS,
    RDUnit,
    TDUnit,
    extract_units,
    find_smallest_unit,
    split_relativedelta_units,
    split_timedelta_units,
)


def idx_exp(style: Style) -> int:
    match style:
        case Style.NORMAL:
            return 0
        case Style.SHORT:
            return 1
        case Style.ABBREV:
            return 2


class TestSplitUnitsTimedelta:
    def test_split_units(self) -> None:
        ans = {
            TDUnit.YEARS: 0,
            TDUnit.WEEKS: 0,
            TDUnit.DAYS: 0,
            TDUnit.HOURS: 0,
            TDUnit.MINUTES: 0,
            TDUnit.SECONDS: 0,
            TDUnit.MICROSECONDS: 0,
            TDUnit.MILLISECONDS: 0,
        }
        delta = timedelta(weeks=53, hours=1, minutes=1)
        assert split_timedelta_units(delta) == {
            **ans,
            TDUnit.YEARS: 1,
            TDUnit.DAYS: 6,
            TDUnit.HOURS: 1,
            TDUnit.MINUTES: 1,
        }
        assert split_timedelta_units(delta, (TDUnit.WEEKS, TDUnit.DAYS)) == {
            **ans,
            TDUnit.WEEKS: 53,
        }
        assert split_timedelta_units(delta, ("days", "hours")) == {
            **ans,
            TDUnit.DAYS: 371,
            TDUnit.HOURS: 1,
        }
        assert split_timedelta_units(delta, (TDUnit.MINUTES,)) == {
            **ans,
            TDUnit.MINUTES: 534301,
        }
        assert split_timedelta_units(delta, (TDUnit.SECONDS,)) == {
            **ans,
            TDUnit.SECONDS: 32058060,
        }
        assert split_timedelta_units(delta, (TDUnit.DAYS, TDUnit.MINUTES)) == {
            **ans,
            TDUnit.DAYS: 371,
            TDUnit.MINUTES: 61,
        }
        assert split_timedelta_units(delta, (TDUnit.DAYS, TDUnit.SECONDS)) == {
            **ans,
            TDUnit.DAYS: 371,
            TDUnit.SECONDS: 3660,
        }
        assert split_timedelta_units(delta, (TDUnit.DAYS, TDUnit.MILLISECONDS)) == {
            **ans,
            TDUnit.DAYS: 371,
            TDUnit.MILLISECONDS: 3660000,
        }
        assert split_timedelta_units(delta, (TDUnit.WEEKS, TDUnit.MICROSECONDS)) == {
            **ans,
            TDUnit.WEEKS: 53,
            TDUnit.MICROSECONDS: 3660000000,
        }

        delta = timedelta(seconds=1)
        assert split_timedelta_units(delta, (TDUnit.DAYS,)) == {
            **ans,
            # TDUnit.SECONDS: 0,
        }

    def test_invalid_keys(self) -> None:
        msg = f"keys can only be the following: {tuple(TDUnit)}"
        with pytest.raises(ValueError, match=re.escape(msg)):
            split_timedelta_units(timedelta(0), units=["bogus"])  # type: ignore[arg-type]


class TestSplitUnitsRelativedelta:
    def test_split_units(self) -> None:
        ans = {
            RDUnit.YEARS: 0,
            RDUnit.MONTHS: 0,
            RDUnit.WEEKS: 0,
            RDUnit.DAYS: 0,
            RDUnit.HOURS: 0,
            RDUnit.MINUTES: 0,
            RDUnit.SECONDS: 0,
            RDUnit.MICROSECONDS: 0,
        }

        delta = relativedelta(months=4, days=14)
        assert split_relativedelta_units(delta) == {
            **ans,
            RDUnit.MONTHS: 4,
            RDUnit.WEEKS: 2,
        }
        delta = relativedelta(weeks=1)
        assert split_relativedelta_units(delta) == {
            **ans,
            RDUnit.WEEKS: 1,
        }
        delta = relativedelta(weeks=6)
        assert split_relativedelta_units(delta) == {
            **ans,
            RDUnit.WEEKS: 6,
        }
        delta = relativedelta(months=1)
        assert split_relativedelta_units(delta) == {
            **ans,
            RDUnit.MONTHS: 1,
        }
        delta = relativedelta(months=15)
        assert split_relativedelta_units(delta) == {
            **ans,
            RDUnit.YEARS: 1,
            RDUnit.MONTHS: 3,
        }
        delta = relativedelta(days=32)
        assert split_relativedelta_units(delta) == {
            **ans,
            RDUnit.WEEKS: 4,
            RDUnit.DAYS: 4,
        }
        delta = relativedelta(years=1)
        assert split_relativedelta_units(delta, (RDUnit.MONTHS,)) == {
            **ans,
            RDUnit.MONTHS: 12,
        }
        delta = relativedelta(weeks=1)
        assert split_relativedelta_units(delta, (RDUnit.DAYS,)) == {
            **ans,
            RDUnit.DAYS: 7,
        }
        delta = relativedelta(years=1, months=2, weeks=53, hours=1, minutes=1)
        assert split_relativedelta_units(delta) == {
            **ans,
            RDUnit.YEARS: 1,
            RDUnit.MONTHS: 2,
            RDUnit.WEEKS: 53,
            RDUnit.HOURS: 1,
            RDUnit.MINUTES: 1,
        }
        assert split_relativedelta_units(delta, (RDUnit.WEEKS, RDUnit.DAYS)) == {
            **ans,
            RDUnit.MONTHS: 14,
            RDUnit.WEEKS: 53,
        }
        assert split_relativedelta_units(delta, (RDUnit.DAYS, RDUnit.HOURS)) == {
            **ans,
            RDUnit.MONTHS: 14,
            RDUnit.DAYS: 371,
            RDUnit.HOURS: 1,
        }
        assert split_relativedelta_units(delta, (RDUnit.MINUTES,)) == {
            **ans,
            RDUnit.MONTHS: 14,
            RDUnit.MINUTES: 534301,
        }
        assert split_relativedelta_units(delta, (RDUnit.SECONDS,)) == {
            **ans,
            RDUnit.MONTHS: 14,
            RDUnit.SECONDS: 32058060,
        }
        assert split_relativedelta_units(delta, (RDUnit.DAYS, RDUnit.MINUTES)) == {
            **ans,
            RDUnit.MONTHS: 14,
            RDUnit.DAYS: 371,
            RDUnit.MINUTES: 61,
        }
        assert split_relativedelta_units(delta, (RDUnit.DAYS, RDUnit.SECONDS)) == {
            **ans,
            RDUnit.MONTHS: 14,
            RDUnit.DAYS: 371,
            RDUnit.SECONDS: 3660,
        }
        assert split_relativedelta_units(delta, (RDUnit.DAYS, RDUnit.MICROSECONDS)) == {
            **ans,
            RDUnit.MONTHS: 14,
            RDUnit.DAYS: 371,
            RDUnit.MICROSECONDS: 3660000000,
        }
        assert split_relativedelta_units(
            delta, (RDUnit.WEEKS, RDUnit.MICROSECONDS)
        ) == {
            **ans,
            RDUnit.MONTHS: 14,
            RDUnit.WEEKS: 53,
            RDUnit.MICROSECONDS: 3660000000,
        }

    def test_invalid_keys(self) -> None:
        msg = f"keys can only be the following: {tuple(RDUnit)}"
        with pytest.raises(ValueError, match=re.escape(msg)):
            split_relativedelta_units(timedelta(0), units=["bogus"])  # type: ignore[arg-type]


class TestTimedelta:
    """Test all things related to from_timedelta and timedelta"""

    # @formatter:off
    # fmt: off
    cases: tuple[tuple[tuple[str, str, str], timedelta], ...] = (
        (("1 millisecond",
          "1 msec",
          "1 ms",
          ), timedelta(milliseconds=1)),
        (("2 milliseconds",
          "2 msecs",
          "2 ms",
          ), timedelta(milliseconds=2)),
        (("1 microsecond",
          "1 µsec",
          "1 µs",
          ), timedelta(microseconds=1)),
        (("2 microseconds",
          "2 µsecs",
          "2 µs",
          ), timedelta(microseconds=2)),
        (("1 millisecond and 1 microsecond",
          "1 msec and 1 µsec",
          "1 ms and 1 µs",
          ), timedelta(milliseconds=1, microseconds=1)),
        (("1 millisecond",
          "1 msec",
          "1 ms",
          ), timedelta(milliseconds=1, microseconds=0)),
        (("1 second",
          "1 sec",
          "1 s",
          ), timedelta(seconds=1)),
        (("5 seconds",
          "5 secs",
          "5 s",
          ), timedelta(seconds=5)),
        (("1 minute",
          "1 min",
          "1 m",
          ), timedelta(minutes=1)),
        (("5 minutes",
          "5 mins",
          "5 m",
          ), timedelta(minutes=5)),
        (("1 minute and 10 seconds",
          "1 min and 10 secs",
          "1 m and 10 s",
          ), timedelta(minutes=1, seconds=10)),
        (("1 hour",
          "1 hr",
          "1 h",
          ), timedelta(hours=1)),
        (("1 hour and 1 second",
          "1 hr and 1 sec",
          "1 h and 1 s",
          ), timedelta(hours=1, seconds=1)),
        (("1 hour and 1 minute",
          "1 hr and 1 min",
          "1 h and 1 m",
          ), timedelta(hours=1, minutes=1)),
        (("2 hours, 1 minute and 1 second",
          "2 hrs, 1 min and 1 sec",
          "2 h, 1 m and 1 s",
          ), timedelta(hours=2, minutes=1, seconds=1)),
        (("1 day",
          "1 day",
          "1 D",
          ), timedelta(days=1)),
        (("2 days",
          "2 days",
          "2 D",
          ), timedelta(days=2)),
        (("1 week",
          "1 wk",
          "1 W",
          ), timedelta(weeks=1)),
        (("2 weeks",
          "2 wks",
          "2 W",
          ), timedelta(weeks=2)),
        (("3 weeks",
          "3 wks",
          "3 W",
          ), timedelta(weeks=2, days=7)),
        (("1 week and 1 second",
          "1 wk and 1 sec",
          "1 W and 1 s",
          ), timedelta(weeks=1, seconds=1)),
        (("1 week and 1 minute",
          "1 wk and 1 min",
          "1 W and 1 m",
          ), timedelta(weeks=1, minutes=1)),
        (("1 week and 1 hour",
          "1 wk and 1 hr",
          "1 W and 1 h",
          ), timedelta(weeks=1, hours=1)),
        (("2 weeks and 2 days",
          "2 wks and 2 days",
          "2 W and 2 D",
          ), timedelta(weeks=2, days=2)),
        (("1 week, 1 hour, 1 minute and 1 second",
          "1 wk, 1 hr, 1 min and 1 sec",
          "1 W, 1 h, 1 m and 1 s",
          ), timedelta(weeks=1, hours=1, minutes=1, seconds=1)),
        (("1 year and 1 hour",
          "1 yr and 1 hr",
          "1 Y and 1 h",
          ), timedelta(days=365, hours=1)),
        (("1 year, 1 week and 3 days",
          "1 yr, 1 wk and 3 days",
          "1 Y, 1 W and 3 D",
          ), timedelta(days=375)),
        (("1 year, 2 weeks and 2 days",
          "1 yr, 2 wks and 2 days",
          "1 Y, 2 W and 2 D",
          ), timedelta(days=367, weeks=2)),
        (("52 weeks and 1 hour",
          "52 wks and 1 hr",
          "52 W and 1 h",
          ), timedelta(weeks=52, hours=1)),
        (("1 year, 6 days and 1 hour",
          "1 yr, 6 days and 1 hr",
          "1 Y, 6 D and 1 h",
          ), timedelta(weeks=53, hours=1)),
        (("1 year, 7 weeks, 6 days and 1 hour",
          "1 yr, 7 wks, 6 days and 1 hr",
          "1 Y, 7 W, 6 D and 1 h",
          ), timedelta(weeks=60, hours=1)),
    )
    # fmt: on
    # @formatter:on

    def _td_signed(self, style: Style) -> None:
        for expected, delta in self.cases:
            assert (
                from_timedelta(delta, include_sign=True, style=style)
                == expected[idx_exp(style)]
            )

    def _td_signed_negative(self, style: Style) -> None:
        for expected, delta in self.cases:
            assert (
                from_timedelta(-delta, include_sign=True, style=style)
                == f"-{expected[idx_exp(style)]}"
            )

    def _td_unsigned(self, style: Style) -> None:
        for expected, delta in self.cases:
            assert (
                from_timedelta(delta, include_sign=False, style=style)
                == expected[idx_exp(style)]
            )

    def _td_unsigned_negative(self, style: Style) -> None:
        for expected, delta in self.cases:
            assert (
                from_timedelta(-delta, include_sign=False, style=style)
                == f"{expected[idx_exp(style)]}"
            )

    def test_signed_normal(self) -> None:
        self._td_signed(Style.NORMAL)

    def test_signed_negative_normal(self) -> None:
        self._td_signed_negative(Style.NORMAL)

    def test_signed_short(self) -> None:
        self._td_signed(Style.SHORT)

    def test_signed_negative_short(self) -> None:
        self._td_signed_negative(Style.SHORT)

    def test_signed_abbrev(self) -> None:
        self._td_signed(Style.ABBREV)

    def test_signed_negative_abbrev(self) -> None:
        self._td_signed_negative(Style.ABBREV)

    def test_unsigned_normal(self) -> None:
        self._td_unsigned(Style.NORMAL)

    def test_unsigned_negative_normal(self) -> None:
        self._td_unsigned_negative(Style.NORMAL)

    def test_usigned_short(self) -> None:
        self._td_unsigned(Style.SHORT)

    def test_usigned_negative_short(self) -> None:
        self._td_unsigned_negative(Style.SHORT)

    def test_unsigned_abbrev(self) -> None:
        self._td_unsigned(Style.ABBREV)

    def test_unsigned_negative_abbrev(self) -> None:
        self._td_unsigned_negative(Style.ABBREV)

    def test_show_zero(self) -> None:
        assert from_timedelta(timedelta(weeks=60, hours=1), showzero=True) == (
            "1 year, 7 weeks, 6 days, 1 hour, 0 minutes, "
            "0 seconds, 0 milliseconds and 0 microseconds"
        )

    def test_from_timedelta_using_relativedelta(self) -> None:
        msg = "'<' not supported between instances of 'relativedelta' and 'datetime.timedelta'"
        with pytest.raises(TypeError, match=msg):
            from_timedelta(relativedelta(hours=0), style=Style.NORMAL)  # type: ignore[arg-type]

    def _td_keys(
        self,
        key_cases: (
            list[tuple[tuple[TDUnit, ...], str]] | list[tuple[tuple[str, ...], str]]
        ),
        delta: timedelta,
        showzero: bool = False,
        style: Style = Style.NORMAL,
    ) -> None:
        for keys, expected in key_cases:
            assert from_timedelta(delta, style, keys, showzero=showzero) == expected

    def test_limited_keys(self) -> None:
        delta = timedelta(weeks=60, hours=1)
        key_cases = [
            ((TDUnit.HOURS,), "10081 hours"),
            ((TDUnit.DAYS, TDUnit.HOURS), "420 days and 1 hour"),
            ((TDUnit.MINUTES,), "604860 minutes"),
            ((TDUnit.SECONDS,), "36291600 seconds"),
            ((TDUnit.MINUTES, TDUnit.SECONDS), "604860 minutes"),
        ]
        self._td_keys(key_cases, delta)

    def test_limited_keys2(self) -> None:
        delta = timedelta(days=6, hours=23, minutes=59, seconds=59)
        # @formatter:off
        # fmt: off
        key_cases = [
            ((TDUnit.DAYS, TDUnit.HOURS, TDUnit.MINUTES, TDUnit.SECONDS),
             "6 days, 23 hours, 59 minutes and 59 seconds"),
            ((TDUnit.HOURS, TDUnit.MINUTES, TDUnit.SECONDS),
             "167 hours, 59 minutes and 59 seconds"),
            ((TDUnit.HOURS,),
             "167 hours"),
            ((TDUnit.MINUTES, TDUnit.SECONDS),
             "10079 minutes and 59 seconds"),
            ((TDUnit.SECONDS,),
             "604799 seconds"),
            ((TDUnit.DAYS, TDUnit.SECONDS),
             "6 days and 86399 seconds"),
        ]
        # fmt: on
        # @formatter:on
        self._td_keys(key_cases, delta)

    def test_limited_keys3(self) -> None:
        """
        Doesn't matter what keys you send when the delta is 0,
        you'll always get back '0 seconds'
        """
        delta = timedelta(0)
        cases_normal = [
            (("hours",), "0 seconds"),
            (("days", "hours"), "0 seconds"),
            (("minutes",), "0 seconds"),
            (("seconds",), "0 seconds"),
            (("minutes", "seconds"), "0 seconds"),
        ]

        self._td_keys(cases_normal, delta, False, Style.NORMAL)

    def test_limited_keys4(self) -> None:
        """
        Doesn't matter what keys you send when the delta is 0,
        you'll always get back '0 secs'
        """
        delta = timedelta(0)
        cases_short = [
            (("hours",), "0 secs"),
            (("days", "hours"), "0 secs"),
            (("minutes",), "0 secs"),
            (("seconds",), "0 secs"),
            (("minutes", "seconds"), "0 secs"),
        ]

        self._td_keys(cases_short, delta, False, Style.SHORT)

    def test_limited_keys5(self) -> None:
        """
        Doesn't matter what keys you send when the delta is 0,
        you'll always get back '0 s'
        """
        delta = timedelta(0)
        cases_abbrev = [
            (("hours",), "0 s"),
            (("days", "hours"), "0 s"),
            (("minutes",), "0 s"),
            (("seconds",), "0 s"),
            (("minutes", "seconds"), "0 s"),
        ]

        self._td_keys(cases_abbrev, delta, False, Style.ABBREV)

    def test_limited_keys_showzero(self) -> None:
        delta = timedelta(days=6, hours=23, minutes=59)
        # @formatter:off
        # fmt: off
        key_cases = [
            (("days", "hours", "minutes", "seconds"),
             "6 days, 23 hours, 59 minutes and 0 seconds"),
            (("hours", "minutes", "seconds", "milliseconds"),
             "167 hours, 59 minutes, 0 seconds and 0 milliseconds"),
            (("weeks", "hours"),
             "0 weeks and 167 hours"),
            (("minutes", "seconds"),
             "10079 minutes and 0 seconds"),
            (("seconds",),
             "604740 seconds"),
            (("days", "seconds"),
             "6 days and 86340 seconds"),
        ]
        # fmt: on
        # @formatter:on
        self._td_keys(key_cases, delta, True)

    def test_limited_keys_showzero2(self) -> None:
        delta = timedelta(0)
        key_cases = [
            (("hours",), "0 hours"),
            (("days", "hours"), "0 days and 0 hours"),
            (("minutes",), "0 minutes"),
            (("seconds",), "0 seconds"),
            (("minutes", "seconds"), "0 minutes and 0 seconds"),
        ]
        self._td_keys(key_cases, delta, True)

    def test_invalid_keys(self) -> None:
        msg = f"keys can only be the following: {tuple(TDUnit)}"
        with pytest.raises(ValueError, match=re.escape(msg)):
            from_timedelta(timedelta(0), units=["bogus"])  # type: ignore[arg-type]

    def test_valid_keys(self) -> None:
        valid = (
            "years",
            "weeks",
            "days",
            "hours",
            "minutes",
            "seconds",
            "milliseconds",
            "microseconds",
        )
        assert from_timedelta(timedelta(0), units=valid) == "0 seconds"
        assert from_timedelta(timedelta(0)) == "0 seconds"

    def test_no_keys(self) -> None:
        delta = timedelta(weeks=60, hours=1)
        key_cases = [
            ((), "1 year, 7 weeks, 6 days and 1 hour"),
        ]
        self._td_keys(key_cases, delta)  # type: ignore[arg-type]

    def test_invalid_style(self) -> None:
        with pytest.raises(ValueError, match="Invalid argument foobar"):
            from_timedelta(timedelta(1), style="foobar")  # type: ignore[arg-type]

    def test_no_output(self) -> None:
        assert from_timedelta(timedelta(seconds=1), units=(TDUnit.HOURS,)) == "NaN"


class TestExtractUnits:
    def test_extract_units(self) -> None:
        assert extract_units(timedelta(hours=28)) == (TDUnit.DAYS, TDUnit.HOURS)
        assert extract_units(timedelta(minutes=90)) == (TDUnit.HOURS, TDUnit.MINUTES)
        assert extract_units(timedelta(minutes=90), units=(TDUnit.MINUTES,)) == (
            TDUnit.MINUTES,
        )
        assert extract_units(timedelta(minutes=60)) == (TDUnit.HOURS,)

    def test_invalid_keys(self) -> None:
        msg = f"keys can only be the following: {tuple(TDUnit)}"
        with pytest.raises(ValueError, match=re.escape(msg)):
            extract_units(timedelta(0), units=["bogus"])  # type: ignore[arg-type]


class TestRelativedelta:
    # fmt: off
    rd_cases: tuple[tuple[tuple[str, str, str], relativedelta], ...] = (
        (("1 microsecond",
          "1 µsec",
          "1 µs",
          ), relativedelta(microseconds=1)),
        (("2 microseconds",
          "2 µsecs",
          "2 µs",
          ), relativedelta(microseconds=2)),
        (("1 second and 1 microsecond",
          "1 sec and 1 µsec",
          "1 s and 1 µs",
          ), relativedelta(seconds=1, microseconds=1)),
        (("1 second",
          "1 sec",
          "1 s",
          ), relativedelta(seconds=1)),
        (("5 seconds",
          "5 secs",
          "5 s",
          ), relativedelta(seconds=5)),
        (("1 minute",
          "1 min",
          "1 m",
          ), relativedelta(minutes=1)),
        (("5 minutes",
          "5 mins",
          "5 m",
          ), relativedelta(minutes=5)),
        (("1 minute and 10 seconds",
          "1 min and 10 secs",
          "1 m and 10 s",
          ), relativedelta(minutes=1, seconds=10)),
        (("1 hour",
          "1 hr",
          "1 h",
          ), relativedelta(hours=1)),
        (("1 hour and 1 second",
          "1 hr and 1 sec",
          "1 h and 1 s",
          ), relativedelta(hours=1, seconds=1)),
        (("1 hour and 1 minute",
          "1 hr and 1 min",
          "1 h and 1 m",
          ), relativedelta(hours=1, minutes=1)),
        (("2 hours, 1 minute and 1 second",
          "2 hrs, 1 min and 1 sec",
          "2 h, 1 m and 1 s",
          ), relativedelta(hours=2, minutes=1, seconds=1)),
        (("1 day",
          "1 day",
          "1 D",
          ), relativedelta(days=1)),
        (("2 days",
          "2 days",
          "2 D",
          ), relativedelta(days=2)),
        (("1 week",
          "1 wk",
          "1 W",
          ), relativedelta(weeks=1)),
        (("2 weeks",
          "2 wks",
          "2 W",
          ), relativedelta(weeks=2)),
        (("1 week and 1 second",
          "1 wk and 1 sec",
          "1 W and 1 s",
          ), relativedelta(weeks=1, seconds=1)),
        (("1 week and 1 minute",
          "1 wk and 1 min",
          "1 W and 1 m",
          ), relativedelta(weeks=1, minutes=1)),
        (("1 week and 1 hour",
          "1 wk and 1 hr",
          "1 W and 1 h",
          ), relativedelta(weeks=1, hours=1)),
        (("2 weeks and 2 days",
          "2 wks and 2 days",
          "2 W and 2 D",
          ), relativedelta(weeks=2, days=2)),
        (("1 week, 1 hour, 1 minute and 1 second",
          "1 wk, 1 hr, 1 min and 1 sec",
          "1 W, 1 h, 1 m and 1 s",
          ), relativedelta(weeks=1, hours=1, minutes=1, seconds=1)),
        (("52 weeks, 1 day and 1 hour",
          "52 wks, 1 day and 1 hr",
          "52 W, 1 D and 1 h",
          ), relativedelta(days=365, hours=1)),
        (("1 month",
          "1 mnth",
          "1 M",
          ), relativedelta(months=1)),
        (("2 months",
          "2 mnths",
          "2 M",
          ), relativedelta(months=2)),
        (("2 months and 1 week",
          "2 mnths and 1 wk",
          "2 M and 1 W",
          ), relativedelta(months=2, days=7)),
        (("53 weeks and 4 days",
          "53 wks and 4 days",
          "53 W and 4 D",
          ), relativedelta(days=375)),
        (("54 weeks and 3 days",
          "54 wks and 3 days",
          "54 W and 3 D",
          ), relativedelta(days=367, weeks=2)),
        (("52 weeks and 1 hour",
          "52 wks and 1 hr",
          "52 W and 1 h",
          ), relativedelta(weeks=52, hours=1)),
        (("53 weeks and 1 hour",
          "53 wks and 1 hr",
          "53 W and 1 h",
          ), relativedelta(weeks=53, hours=1)),
        (("60 weeks and 1 hour",
          "60 wks and 1 hr",
          "60 W and 1 h",
          ), relativedelta(weeks=60, hours=1)),
    )
    # fmt: on

    def _rd_signed(self, style: Style) -> None:
        for expected, delta in self.rd_cases:
            assert (
                from_relativedelta(delta, include_sign=True, style=style)
                == expected[idx_exp(style)]
            )

    def _rd_signed_negative(self, style: Style) -> None:
        for expected, delta in self.rd_cases:
            assert (
                from_relativedelta(-delta, include_sign=True, style=style)
                == f"-{expected[idx_exp(style)]}"
            )

    def _rd_unsigned(self, style: Style) -> None:
        for expected, delta in self.rd_cases:
            assert (
                from_relativedelta(delta, include_sign=False, style=style)
                == expected[idx_exp(style)]
            )

    def _rd_unsigned_negative(self, style: Style) -> None:
        for expected, delta in self.rd_cases:
            assert (
                from_relativedelta(-delta, include_sign=False, style=style)
                == f"{expected[idx_exp(style)]}"
            )

    def test_signed_normal(self) -> None:
        self._rd_signed(Style.NORMAL)

    def test_signed_negative_normal(self) -> None:
        self._rd_signed_negative(Style.NORMAL)

    def test_signed_short(self) -> None:
        self._rd_signed(Style.SHORT)

    def test_signed_negative_short(self) -> None:
        self._rd_signed_negative(Style.SHORT)

    def test_signed_abbrev(self) -> None:
        self._rd_signed(Style.ABBREV)

    def test_signed_negative_abbrev(self) -> None:
        self._rd_signed_negative(Style.ABBREV)

    def test_unsigned_normal(self) -> None:
        self._rd_unsigned(Style.NORMAL)

    def test_unsigned_negative_normal(self) -> None:
        self._rd_unsigned_negative(Style.NORMAL)

    def test_unsigned_short(self) -> None:
        self._rd_unsigned(Style.SHORT)

    def test_unsigned_negative_short(self) -> None:
        self._rd_unsigned_negative(Style.SHORT)

    def test_unsigned_abbrev(self) -> None:
        self._rd_unsigned(Style.ABBREV)

    def test_unsigned_negative_abbrev(self) -> None:
        self._rd_unsigned_negative(Style.ABBREV)

    def test_show_zero(self) -> None:
        assert from_relativedelta(relativedelta(weeks=60, hours=1), showzero=True) == (
            "0 years, 0 months, 60 weeks, 0 days, 1 hour, 0 minutes, "
            "0 seconds and 0 microseconds"
        )

    def test_from_timedelta_using_relativedelta(self) -> None:
        msg = "'datetime.timedelta' object has no attribute 'years'"
        with pytest.raises(AttributeError, match=msg):
            from_relativedelta(timedelta(hours=0), style=Style.NORMAL)  # type: ignore[arg-type]

    def _rd_keys(
        self,
        key_cases: (
            list[tuple[tuple[RDUnit, ...], str]] | list[tuple[tuple[str, ...], str]]
        ),
        delta: relativedelta,
        showzero: bool = False,
        style: Style = Style.NORMAL,
    ) -> None:
        for keys, expected in key_cases:
            assert from_relativedelta(delta, style, keys, showzero=showzero) == expected

    def test_limited_keys(self) -> None:
        delta = relativedelta(weeks=60, hours=1)
        key_cases = [
            ((RDUnit.HOURS,), "10081 hours"),
            ((RDUnit.DAYS, RDUnit.HOURS), "420 days and 1 hour"),
            ((RDUnit.MINUTES,), "604860 minutes"),
            ((RDUnit.SECONDS,), "36291600 seconds"),
            ((RDUnit.MINUTES, RDUnit.SECONDS), "604860 minutes"),
        ]
        self._rd_keys(key_cases, delta)

    def test_limited_keys2(self) -> None:
        delta = relativedelta(days=6, hours=23, minutes=59, seconds=59)
        # @formatter:off
        # fmt: off
        key_cases = [
            ((RDUnit.DAYS, RDUnit.HOURS, RDUnit.MINUTES, RDUnit.SECONDS),
             "6 days, 23 hours, 59 minutes and 59 seconds"),
            ((RDUnit.HOURS, RDUnit.MINUTES, RDUnit.SECONDS),
             "167 hours, 59 minutes and 59 seconds"),
            ((RDUnit.HOURS,),
             "167 hours"),
            ((RDUnit.MINUTES, RDUnit.SECONDS),
             "10079 minutes and 59 seconds"),
            ((RDUnit.SECONDS,),
             "604799 seconds"),
            ((RDUnit.DAYS, RDUnit.SECONDS),
             "6 days and 86399 seconds"),
        ]
        # fmt: on
        # @formatter:on
        self._rd_keys(key_cases, delta)

    def test_limited_keys3(self) -> None:
        """
        Doesn't matter what keys you send when the delta is 0,
        you'll always get back '0 seconds'
        """
        delta = relativedelta(days=0)
        cases_normal = [
            (("hours",), "0 seconds"),
            (("days", "hours"), "0 seconds"),
            (("minutes",), "0 seconds"),
            (("seconds",), "0 seconds"),
            (("minutes", "seconds"), "0 seconds"),
        ]

        self._rd_keys(cases_normal, delta, False, Style.NORMAL)

    def test_limited_keys4(self) -> None:
        """
        Doesn't matter what keys you send when the delta is 0,
        you'll always get back '0 secs'
        """
        delta = relativedelta(days=0)
        cases_short = [
            (("hours",), "0 secs"),
            (("days", "hours"), "0 secs"),
            (("minutes",), "0 secs"),
            (("seconds",), "0 secs"),
            (("minutes", "seconds"), "0 secs"),
        ]

        self._rd_keys(cases_short, delta, False, Style.SHORT)

    def test_limited_keys5(self) -> None:
        """
        Doesn't matter what keys you send when the delta is 0,
        you'll always get back '0 s'
        """
        delta = relativedelta(days=0)
        cases_abbrev = [
            (("hours",), "0 s"),
            (("days", "hours"), "0 s"),
            (("minutes",), "0 s"),
            (("seconds",), "0 s"),
            (("minutes", "seconds"), "0 s"),
        ]

        self._rd_keys(cases_abbrev, delta, False, Style.ABBREV)

    def test_limited_keys_showzero(self) -> None:
        delta = relativedelta(days=6, hours=23, minutes=59)
        # @formatter:off
        # fmt: off
        key_cases = [
            (("days", "hours", "minutes", "seconds"),
             "6 days, 23 hours, 59 minutes and 0 seconds"),
            (("hours", "minutes", "seconds", "microseconds"),
             "167 hours, 59 minutes, 0 seconds and 0 microseconds"),
            (("weeks", "hours"),
             "0 weeks and 167 hours"),
            (("minutes", "seconds"),
             "10079 minutes and 0 seconds"),
            (("seconds",),
             "604740 seconds"),
            (("days", "seconds"),
             "6 days and 86340 seconds"),
        ]
        # fmt: on
        # @formatter:on
        self._rd_keys(key_cases, delta, True)

    def test_limited_keys_showzero2(self) -> None:
        delta = relativedelta(hours=0)
        key_cases = [
            (("hours",), "0 hours"),
            (("days", "hours"), "0 days and 0 hours"),
            (("minutes",), "0 minutes"),
            (("seconds",), "0 seconds"),
            (("minutes", "seconds"), "0 minutes and 0 seconds"),
        ]
        self._rd_keys(key_cases, delta, True)

    def test_relativedelta_invalid_keys(self) -> None:
        msg = f"keys can only be the following: {tuple(RDUnit)}"
        with pytest.raises(ValueError, match=re.escape(msg)):
            from_relativedelta(relativedelta(hours=0), units=("bogus", "milliseconds"))

    def test_relativedelta_valid_keys(self) -> None:
        valid = (
            "years",
            "months",
            "days",
            "hours",
            "minutes",
            "seconds",
            "microseconds",
        )

        assert from_relativedelta(relativedelta(hours=0), units=valid) == "0 seconds"
        assert from_relativedelta(relativedelta(hours=0)) == "0 seconds"

    def test_no_keys(self) -> None:
        delta = relativedelta(weeks=60, hours=1)
        key_cases = [
            ((), "60 weeks and 1 hour"),
        ]
        self._rd_keys(key_cases, delta)  # type: ignore[arg-type]

    def test_invalid_style(self) -> None:
        with pytest.raises(ValueError, match="Invalid argument foobar"):
            from_relativedelta(relativedelta(days=1), style="foobar")  # type: ignore[arg-type]

    def test_no_output(self) -> None:
        assert (
            from_relativedelta(relativedelta(seconds=1), units=(RDUnit.HOURS,)) == "NaN"
        )


def test_smallest_unit() -> None:
    assert find_smallest_unit((YEARS,)) is YEARS
    assert find_smallest_unit((YEARS, MONTHS)) is MONTHS
    assert find_smallest_unit((MONTHS, WEEKS)) is WEEKS
    assert find_smallest_unit((WEEKS, DAYS)) is DAYS
    assert find_smallest_unit((DAYS, HOURS)) is HOURS
    assert find_smallest_unit((HOURS, MINUTES)) is MINUTES
    assert find_smallest_unit((MINUTES, SECONDS)) is SECONDS
    assert find_smallest_unit((SECONDS, MILLISECONDS)) is MILLISECONDS
    assert find_smallest_unit((MILLISECONDS, MICROSECONDS)) is MICROSECONDS


def test_smallest_unit_tdunit() -> None:
    assert (
        find_smallest_unit((TDUnit.YEARS, TDUnit.SECONDS, TDUnit.DAYS))
        is TDUnit.SECONDS
    )
    assert find_smallest_unit((TDUnit.YEARS, TDUnit.DAYS)) is TDUnit.DAYS
    assert (
        find_smallest_unit((TDUnit.YEARS, TDUnit.MINUTES, TDUnit.DAYS))
        is TDUnit.MINUTES
    )
    assert find_smallest_unit((TDUnit.YEARS, TDUnit.WEEKS, TDUnit.DAYS)) is TDUnit.DAYS


def test_smallest_unit_rdunit() -> None:
    assert (
        find_smallest_unit((RDUnit.YEARS, RDUnit.SECONDS, RDUnit.DAYS))
        is RDUnit.SECONDS
    )
    assert find_smallest_unit((RDUnit.YEARS, RDUnit.DAYS)) is RDUnit.DAYS
    assert (
        find_smallest_unit((RDUnit.YEARS, RDUnit.MINUTES, RDUnit.DAYS))
        is RDUnit.MINUTES
    )
    assert (
        find_smallest_unit((RDUnit.YEARS, RDUnit.MONTHS, RDUnit.WEEKS)) is RDUnit.WEEKS
    )


def test_smallest_unit_invalid() -> None:
    with pytest.raises(ValueError, match="Unknown units"):
        find_smallest_unit(("years", "seconds", "days", "wibblies"))

    class FAKEUnit(StrEnum):
        YEARS = "years"
        WEEKS = "weeks"
        FOO = "foo"

    assert find_smallest_unit((FAKEUnit.YEARS, FAKEUnit.WEEKS)) is FAKEUnit.WEEKS
    with pytest.raises(ValueError, match="Unknown units"):
        find_smallest_unit((FAKEUnit.YEARS, FAKEUnit.WEEKS, FAKEUnit.FOO))
