"""Provide common types for statechart components."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Optional, Sequence, Union

from superstate.model.base import Action, Conditional
from superstate.types import Expression

if TYPE_CHECKING:
    from superstate.provider import Provider
    from superstate.model.base import ExecutableContent
    from superstate.model.system import Event


@dataclass
class Assign(Action):
    """Data item providing state data."""

    location: str
    expr: Optional[Expression] = None  # expression

    def callback(
        self, provider: 'Provider', *args: Any, **kwargs: Any
    ) -> None:
        """Provide callback from datamodel provider."""
        provider.exec(self.expr, *args, **kwargs)
        # print(result)
        # setattr(self.ctx, expr.location, expr)


@dataclass
class ForEach(Action):
    """Data item providing state data."""

    array: Sequence[Action]
    item: Optional[str]
    index: Optional[str] = None  # expression

    def __post_init__(self) -> None:
        self.array = [Action.create(x) for x in self.array]

    def callback(
        self, provider: 'Provider', *args: Any, **kwargs: Any
    ) -> None:
        """Provide callback from datamodel provider."""


@dataclass
class Log(Action):
    """Data item providing state data."""

    expr: Expression
    label: Optional[str] = None

    def callback(
        self, provider: 'Provider', *args: Any, **kwargs: Any
    ) -> None:
        """Provide callback from datamodel provider."""


@dataclass
class Raise(Action):
    """Data item providing state data."""

    event: 'Event'

    def callback(
        self, provider: 'Provider', *args: Any, **kwargs: Any
    ) -> None:
        """Provide callback from datamodel provider."""


@dataclass
class Script(Action):
    """Data model providing para data for external services."""

    # XXX: should include buffer or replace string
    src: Union[Callable, str]

    def callback(
        self, provider: 'Provider', *args: Any, **kwargs: Any
    ) -> Optional[Any]:
        """Provide callback from datamodel provider."""
        return provider.exec(self.src, *args, **kwargs)


@dataclass
class If(Conditional):
    """Data item providing state data."""

    actions: Sequence['ExecutableContent']

    def __post_init__(self) -> None:
        self.actions = [Action.create(x) for x in self.actions]

    def callback(
        self, provider: 'Provider', *args: Any, **kwargs: Any
    ) -> Optional[Any]:
        """Provide callback from datamodel provider."""
        if provider.eval(self.cond, *args, **kwargs):
            for action in self.actions:
                return provider.handle(action, *args, **kwargs)
        return None


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

    def callback(
        self, provider: 'Provider', *args: Any, **kwargs: Any
    ) -> None:
        """Provide callback from datamodel provider."""
        for action in self.actions:
            provider.handle(action)
