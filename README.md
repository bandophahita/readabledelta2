Readable Timedelta (mark2)
==========================
[![Tests Status](https://github.com/bandophahita/readabledelta2/actions/workflows/tests.yml/badge.svg)](https://github.com/bandophahita/readabledelta2/actions/workflows/tests.yml)
[![Lint Status](https://github.com/bandophahita/readabledelta2/actions/workflows/lint.yml/badge.svg)](https://github.com/bandophahita/readabledelta2/actions/workflows/lint.yml)

[![Supported Versions](https://img.shields.io/pypi/pyversions/readabledelta2.svg)](https://pypi.org/project/readabledelta2)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Installation
------------

```console
pip install readabledelta2
```

Usage examples
--------------

`from_timedelta` creates a more human-friendly printable version of `timedelta`.
```python
>>> delta = timedelta(weeks=53, hours=1, minutes=1)
>>> f"Update was {delta} ago"
'Update was 371 days, 1:01:00 ago'
>>> f"Update was {from_timedelta(delta)} ago"
'Update was 1 year, 6 days, 1 hour and 1 minute ago'
```

For negative timedeltas, the default representation is more machine-friendly than 
human-friendly: 
"an hour and five minutes" is easier for people to understand than 
the weird but technically-correct 
"negative one day plus 22 hours and 55 minutes"

```python
>>> lunchtime = datetime(year=2015, month=5, day=27, hour=12)
>>> right_now = datetime(year=2015, month=5, day=27, hour=13, minute=5)
>>> f"{lunchtime - right_now}"
'-1 day, 22:55:00'
>>> f"{from_timedelta(lunchtime - right_now)}"
'-1 hour and 5 minutes'
```

`from_timedelta` has customization options

Show all units even those without a value
```python
>>> print(from_timedelta(timedelta(weeks=60, hours=1), showzero=True))
'1 year, 7 weeks, 6 days, 1 hour, 0 minutes, 0 seconds, 0 milliseconds and 0 microseconds'
```

Output using only specific units

```python
>>> delta = timedelta(days=6, hours=23, minutes=59, seconds=59)
>>> print(from_timedelta(delta), units=['days', 'seconds'])
'6 days and 86399 seconds'
```

Contributing
------------

You want to contribute? Great! Here are the things you should do before submitting your PR:

1. Fork the repo and git clone your fork.
1. `dev` install the project package:
   1. `pip install -e .[dev]`
   1. Optional (poetry users):
      1. `poetry install --extras dev`
1. Run `tox` to perform tests frequently.
1. Create pull-request from your branch.

That's it! :)
