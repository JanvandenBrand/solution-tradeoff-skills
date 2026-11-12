"""Parse the dates in a run record, the same way for every script.

A date must be written as YYYY-MM-DD without quotes, so YAML reads it as a
date. A quoted date is text, and a date with a time is a timestamp; both are
rejected, so the run-record validator and the verification gate agree.
"""

from datetime import date
from typing import Any


def parse_date(value: Any, field: str) -> date:
    """Return ``value`` if YAML read it as a date.

    Args:
        value: The parsed YAML value.
        field: The field name, used in the error message.

    Raises:
        ValueError: If ``value`` is not a date, including a quoted date or a
            date with a time.
    """
    if type(value) is date:
        return value
    raise ValueError(f"{field} must be a date written as YYYY-MM-DD without quotes, got {value!r}")
