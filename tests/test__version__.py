from __future__ import annotations

from readabledelta2 import __version__


def test_metadata() -> None:
    assert __version__.__title__ == "readabledelta2"
    assert __version__.__license__ == "MIT"
    assert __version__.__author__ == "Marcel Wilson"
