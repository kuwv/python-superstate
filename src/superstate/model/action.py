"""Provide common types for statechart components."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Sequence

from superstate.model.base import Action

if TYPE_CHECKING:
    from superstate.model.system import Event


@dataclass
class Assign(Action):
    """Data item providing state data."""

    location: str
    expr: Optional[str] = None  # expression


@dataclass
class If(Action):
    """Data item providing state data."""

    cond: str
    actions: Sequence[Action]

    def __post_init__(self) -> None:
        self.actions = [Action.create(x) for x in self.actions]


@dataclass
class ElseIf(If):
    """Data item providing state data."""


@dataclass
class Else(Action):
    """Data item providing state data."""

    actions: Sequence[Action]

    def __post_init__(self) -> None:
        self.actions = [Action.create(x) for x in self.actions]


@dataclass
class ForEach(Action):
    """Data item providing state data."""

    array: Sequence[Action]
    item: Optional[str]
    index: Optional[str] = None  # expression

    def __post_init__(self) -> None:
        self.array = [Action.create(x) for x in self.array]


@dataclass
class Log(Action):
    """Data item providing state data."""

    expr: str  # expression
    label: Optional[str] = None


@dataclass
class Raise(Action):
    """Data item providing state data."""

    event: 'Event'


# @dataclass
# class Script:
#     """Data model providing para data for external services."""
#
#     src: str
