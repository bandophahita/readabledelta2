from __future__ import annotations

from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from readabledelta2 import Style, from_relativedelta, to_string
from readabledelta2.readabledelta import (
    RDUnit,
    TDUnit,
    extract_units,
    split_relativedelta_units,
    split_timedelta_units,
)


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


class TestTimedelta:
    """Test all things related to to_string and timedelta"""

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
            assert to_string(delta, include_sign=True, style=style) == expected[style]

        for expected, delta in self.cases:
            assert (
                to_string(-delta, include_sign=True, style=style)
                == f"-{expected[style]}"
            )

    def _td_unsigned(self, style: Style) -> None:
        for expected, delta in self.cases:
            assert to_string(delta, include_sign=False, style=style) == expected[style]

        for expected, delta in self.cases:
            assert (
                to_string(-delta, include_sign=False, style=style)
                == f"{expected[style]}"
            )

    def test_signed_normal(self) -> None:
        self._td_signed(Style.NORMAL)

    def test_unsigned_normal(self) -> None:
        self._td_unsigned(Style.NORMAL)

    def test_signed_short(self) -> None:
        self._td_signed(Style.SHORT)

    def test_usigned_short(self) -> None:
        self._td_unsigned(Style.SHORT)

    def test_signed_abbrev(self) -> None:
        self._td_signed(Style.ABBREV)

    def test_unsigned_abbrev(self) -> None:
        self._td_unsigned(Style.ABBREV)

    def test_show_zero(self) -> None:
        assert to_string(timedelta(weeks=60, hours=1), showzero=True) == (
            "1 year, 7 weeks, 6 days, 1 hour, 0 minutes, "
            "0 seconds, 0 milliseconds and 0 microseconds"
        )

    def test_to_string_using_relativedelta(self) -> None:
        with pytest.raises(TypeError):
            to_string(relativedelta(hours=0), style=Style.NORMAL)  # type: ignore[arg-type]

    def _td_keys(
        self,
        # key_cases: list[tuple[tuple[TDUnit, ...], str]],
        # key_cases: list[tuple[tuple[TDUnit, ...] | tuple[str, ...], str]],
        # key_cases: list[tuple[tuple[TDUnit, ...] | tuple[T_tdkeys, ...], str]],
        # key_cases: list[tuple[tuple[TDUnit | str, ...], str]],
        # key_cases: list[tuple[tuple[TDUnit | T_tdkeys, ...], str]],
        key_cases: (
            list[tuple[tuple[TDUnit, ...], str]] | list[tuple[tuple[str, ...], str]]
        ),
        # key_cases: list[tuple[Sequence[TDUnit] | Sequence[T_tdkeys], ...], str],
        delta: timedelta,
        showzero: bool = False,
    ) -> None:
        for keys, expected in key_cases:
            assert to_string(delta, keys=keys, showzero=showzero) == expected

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
        you'll always get back the delta
        """
        delta = timedelta(0)
        key_cases = [
            (("hours",), "0:00:00"),
            (("days", "hours"), "0:00:00"),
            (("minutes",), "0:00:00"),
            (("seconds",), "0:00:00"),
            (("minutes", "seconds"), "0:00:00"),
        ]
        self._td_keys(key_cases, delta, False)

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
        with pytest.raises(AssertionError):
            to_string(timedelta(0), keys=["bogus"])  # type: ignore[arg-type]

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
        assert to_string(timedelta(0), keys=valid) == "0:00:00"
        assert to_string(timedelta(0)) == "0:00:00"


class TestExtractUnits:
    def test_extract_units(self) -> None:
        assert extract_units(timedelta(hours=28)) == (TDUnit.DAYS, TDUnit.HOURS)
        assert extract_units(timedelta(minutes=90)) == (TDUnit.HOURS, TDUnit.MINUTES)
        assert extract_units(timedelta(minutes=60)) == (TDUnit.HOURS,)


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

    # not supported yet
    def _rd_signed(self, style: Style) -> None:
        for expected, delta in self.rd_cases:
            assert (
                from_relativedelta(delta, include_sign=True, style=style)
                == expected[style]
            )

    def _rd_signed_negative(self, style: Style) -> None:
        for expected, delta in self.rd_cases:
            assert (
                from_relativedelta(-delta, include_sign=True, style=style)
                == f"-{expected[style]}"
            )

    def _rd_unsigned(self, style: Style) -> None:
        for expected, delta in self.rd_cases:
            assert (
                from_relativedelta(delta, include_sign=False, style=style)
                == expected[style]
            )

    def _rd_unsigned_negative(self, style: Style) -> None:
        for expected, delta in self.rd_cases:
            assert (
                from_relativedelta(-delta, include_sign=False, style=style)
                == f"{expected[style]}"
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

    def test_relativedelta_invalid_keys(self) -> None:
        with pytest.raises(AssertionError):
            from_relativedelta(relativedelta(hours=0), keys=("bogus", "milliseconds"))

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
        assert from_relativedelta(relativedelta(hours=0), keys=valid) == "now"
