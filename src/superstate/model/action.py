"""Provide common types for statechart components."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Sequence

from superstate.model.base import Action

if TYPE_CHECKING:
    from superstate.provider import Provider
    from superstate.model.system import Event


@dataclass
class Assign(Action):
    """Data item providing state data."""

    location: str
    expr: Optional[str] = None  # expression

    def callback(self, provider: 'Provider') -> None:
        """Provide callback from datamodel provider."""
        provider.exec(self)


@dataclass
class If(Action):
    """Data item providing state data."""

    cond: str
    actions: Sequence[Action]

    def __post_init__(self) -> None:
        self.actions = [Action.create(x) for x in self.actions]

    def callback(self, provider: 'Provider') -> None:
        """Provide callback from datamodel provider."""
        if provider.eval(self):
            for action in self.actions:
                provider.accept(action)


@dataclass
class ElseIf(If):
    """Data item providing state data."""


@dataclass
class Else(Action):
    """Data item providing state data."""

    actions: Sequence[Action]

    def __post_init__(self) -> None:
        self.actions = [Action.create(x) for x in self.actions]

    def callback(self, provider: 'Provider') -> None:
        """Provide callback from datamodel provider."""
        for action in self.actions:
            provider.accept(action)


@dataclass
class ForEach(Action):
    """Data item providing state data."""

    array: Sequence[Action]
    item: Optional[str]
    index: Optional[str] = None  # expression

    def __post_init__(self) -> None:
        self.array = [Action.create(x) for x in self.array]

    def callback(self, provider: 'Provider') -> None:
        """Provide callback from datamodel provider."""


@dataclass
class Log(Action):
    """Data item providing state data."""

    expr: str  # expression
    label: Optional[str] = None

    def callback(self, provider: 'Provider') -> None:
        """Provide callback from datamodel provider."""


@dataclass
class Raise(Action):
    """Data item providing state data."""

    event: 'Event'

    def callback(self, provider: 'Provider') -> None:
        """Provide callback from datamodel provider."""


# @dataclass
# class Script:
#     """Data model providing para data for external services."""
#
#     src: str
#
#     def callback(self, provider: 'Provider') -> None:
#        """Provide callback from datamodel provider."""
