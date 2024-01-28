"""Provide common utilities."""

from typing import Any, Tuple, Union


def to_bool(value: Union[bool, int, str]) -> bool:
    """Convert a string truth statement to conditional."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        value = value.lower()
    if value in ('y', 'yes', 't', 'true', 'on', '1', 1):
        return True
    if value in ('n', 'no', 'f', 'false', 'off', '0', 0):
        return False
    raise ValueError(f"invalid truth value {value!r}")


def tuplize(value: Any) -> Tuple[Any, ...]:
    """Convert various collection types to tuple."""
    return tuple(value) if type(value) in (list, tuple) else (value,)
