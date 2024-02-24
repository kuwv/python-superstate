"""Provide common types for statechart components."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional, Sequence, Union

from superstate.model.base import Action, Conditional

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


@dataclass
class Script(Action):
    """Data model providing para data for external services."""

    src: Union[Callable, str]

    def callback(self, provider: 'Provider') -> None:
        """Provide callback from datamodel provider."""
        provider.exec(self.src)


@dataclass
class If(Conditional):
    """Data item providing state data."""

    actions: Sequence[Action]

    def __post_init__(self) -> None:
        self.actions = [Action.create(x) for x in self.actions]

    def callback(self, provider: 'Provider') -> None:
        """Provide callback from datamodel provider."""
        if provider.eval(self):
            for action in self.actions:
                provider.run(action)


@dataclass
class ElseIf(If):
    """Data item providing state data."""


@dataclass
class Else(Conditional):
    """Data item providing state data."""

    actions: Sequence[Action]

    def __post_init__(self) -> None:
        self.cond = True
        self.actions = [Action.create(x) for x in self.actions]

    def callback(self, provider: 'Provider') -> None:
        """Provide callback from datamodel provider."""
        for action in self.actions:
            provider.run(action)
