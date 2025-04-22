"""Provide common types for statechart components."""

from __future__ import annotations

import logging
import logging.config
from collections.abc import Callable
from dataclasses import InitVar, asdict, dataclass
from typing import TYPE_CHECKING, Any, Optional, Sequence, Union

from superstate.config import LOGGING_CONFIG
from superstate.model.base import Action, Conditional
from superstate.types import Expression

if TYPE_CHECKING:
    from superstate.provider import Provider
    from superstate.model.base import ExecutableContent
    from superstate.model.system import Event

logging.config.dictConfig(LOGGING_CONFIG)
log = logging.getLogger(__name__)


@dataclass
class Assign(Action):
    """Data item providing state data."""

    location: str
    expr: Optional[Expression] = None  # expression

    def callback(self, provider: Provider, *args: Any, **kwargs: Any) -> None:
        """Provide callback from datamodel provider."""
        kwargs['__mode__'] = 'single'
        result = provider.exec(self.expr, *args, **kwargs)

        if self.location in provider.ctx.current_state.datamodel.keys():
            provider.ctx.current_state.datamodel[self.location] = result
        elif (
            self.location in provider.ctx.datamodel.keys()
            or self.location in asdict(provider.ctx.datamodel).keys()
        ):
            provider.ctx.datamodel[self.location] = result
        else:
            raise AttributeError(
                f"unable to set missing datamodel attribute: {self.location}"
            )


@dataclass
class ForEach(Action):
    """Data item providing state data."""

    content: InitVar[list[str]]
    array: str
    item: str
    index: Optional[str] = None  # expression

    def __post_init__(self, content: list[str]) -> None:
        self.__content = [Action.create(x) for x in content]  # type: ignore

    def callback(self, provider: Provider, *args: Any, **kwargs: Any) -> None:
        """Provide callback from datamodel provider."""
        array = provider.ctx.current_state.datamodel[self.array]
        if array:
            for index, item in enumerate(array):
                for expr in self.__content:
                    if self.index:
                        kwargs[self.index] = index
                    if self.item:
                        kwargs[self.item] = item
                    provider.handle(expr, *args, **kwargs)
        else:
            raise AttributeError(
                'unable to iterate missing datamodel attribute.', self.array
            )


@dataclass
class Log(Action):
    """Data item providing state data."""

    expr: Expression
    label: str = ''
    level: Union[int, str] = 'debug'

    # def __post_init__(self) -> None:
    #     self.__log = logging.getLogger(self.label or provider.ctx.__name__)

    def callback(self, provider: Provider, *args: Any, **kwargs: Any) -> None:
        """Provide callback from datamodel provider."""
        kwargs['__mode__'] = 'single'
        logger = logging.getLogger(self.label)
        logger.setLevel(logging.DEBUG)
        result = provider.exec(self.expr, *args, **kwargs)
        logger.debug(result)


@dataclass
class Raise(Action):
    """Data item providing state data."""

    event: Event

    def callback(self, provider: Provider, *args: Any, **kwargs: Any) -> None:
        """Provide callback from datamodel provider."""
        kwargs['__mode__'] = 'single'


@dataclass
class Script(Action):
    """Data model providing para data for external services."""

    # XXX: src is also URI
    # XXX: should include buffer or replace string
    src: Union[Callable, str]

    def callback(
        self, provider: Provider, *args: Any, **kwargs: Any
    ) -> Optional[Any]:
        """Provide callback from datamodel provider."""
        # need ability to download src URI
        kwargs['__mode__'] = 'exec'
        return provider.exec(self.src, *args, **kwargs)


@dataclass
class If(Conditional):
    """Data item providing state data."""

    content: Sequence[ExecutableContent]

    def __post_init__(self) -> None:
        self.content = [Action.create(x) for x in self.content]

    def callback(
        self, provider: Provider, *args: Any, **kwargs: Any
    ) -> Optional[Any]:
        """Provide callback from datamodel provider."""
        if provider.eval(self.cond, *args, **kwargs):
            for action in self.content:
                return provider.handle(action, *args, **kwargs)
        return None


@dataclass
class ElseIf(If):
    """Data item providing state data."""


@dataclass
class Else(Conditional):
    """Data item providing state data."""

    content: Sequence[Action]

    def __post_init__(self) -> None:
        self.cond = True
        self.content = [Action.create(x) for x in self.content]  # type: ignore

    def callback(self, provider: Provider, *args: Any, **kwargs: Any) -> None:
        """Provide callback from datamodel provider."""
        for action in self.content:
            provider.handle(action, *args, **kwargs)
