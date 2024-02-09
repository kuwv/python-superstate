"""Provide common types for statechart components."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Iterable, Optional

if TYPE_CHECKING:
    from superstate.model.system import Event


@dataclass
class Assign:
    """Data item providing state data."""

    location: str
    expr: Optional[Any] = None  # expression


class If:
    """Data item providing state data."""

    cond: str


class ElseIf:
    """Data item providing state data."""

    cond: str


class Else:
    """Data item providing state data."""


class ForEach:
    """Data item providing state data."""

    array: Iterable[Any]
    item: Optional[str]
    index: Optional[str] = None  # expression


class Log:
    """Data item providing state data."""

    label: str
    expr: Optional[Any] = None  # expression


class Raise:
    """Data item providing state data."""

    event: 'Event'


# class Script:
#     """Data model providing para data for external services."""
#
#     src: str
