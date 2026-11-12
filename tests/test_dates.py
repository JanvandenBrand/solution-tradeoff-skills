"""Unit tests for scripts/dates.py."""

from datetime import date, datetime

import pytest

from dates import parse_date

_MESSAGE = "confirmed_at must be a date written as YYYY-MM-DD without quotes, got "


def test_parse_date_accepts_a_yaml_date():
    assert parse_date(date(2026, 11, 12), "confirmed_at") == date(2026, 11, 12)


@pytest.mark.parametrize(
    "value",
    ["2026-11-12", datetime(2026, 11, 12, 10, 0), 20261112, None, "soon"],
    ids=["quoted", "datetime", "number", "missing", "text"],
)
def test_parse_date_rejects_everything_else_with_one_message(value):
    with pytest.raises(ValueError) as exc:
        parse_date(value, "confirmed_at")
    assert str(exc.value) == _MESSAGE + repr(value)
