"""Provide common types for statechart components."""

import re
from abc import ABC, abstractmethod  # pylint: disable=no-name-in-module
from functools import singledispatchmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Optional,
    Type,
    TypeVar,
    Union,
)

from superstate.exception import InvalidConfig
from superstate.utils import lookup_subclasses

if TYPE_CHECKING:
    from superstate.machine import StateChart
    from superstate.model.base import ExecutableContent

T = TypeVar('T')


class Provider(ABC):
    """Instantiate state types from class metadata."""

    # should support platform-specific, global, and local variables

    def __init__(self, ctx: 'StateChart') -> None:
        """Initialize for MyPy."""
        self.ctx = ctx

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self == other
        if isinstance(other, str):
            return self.__class__.__name__ == other
        return False

    @classmethod
    def get_provider(cls, name: str) -> Type['Provider']:
        """Retrieve a data model implementation."""
        for Subclass in lookup_subclasses(cls):
            if Subclass.__name__.lower() == name.lower():
                return Subclass
        raise InvalidConfig('could not find provider context matching name')

    # @classmethod
    # def create(
    #     cls, ctx: 'StateChart', settings: Union['Provider', str]
    # ) -> 'Provider':
    #     """Factory for data model provider."""
    #     # if isinstance(settings, 'Provider'):
    #     #     return settings
    #     if isinstance(settings, str):
    #         Subclass = cls.get_provider(cls.enabled.lower())
    #         if Subclass:
    #             return Subclass()
    #     raise InvalidConfig(
    #         'could not find a valid data model configuration'
    #     )

    @property
    def globals(self) -> Dict[str, Any]:
        """Get global attributes and methods available for eval and exec."""
        # pylint: disable=import-outside-toplevel
        from datetime import datetime

        return {
            # '__builtins__': {},
            'datetime': datetime
        }

    @property
    def locals(self) -> Dict[str, Any]:
        """Get local attributes and methods available for eval and exec."""
        # return {
        #     x: getattr(self.ctx, x)
        #     for x in dir(self.ctx)
        #     # if not x.startswith('__')
        # }
        lcl = {x.id: x.value for x in self.ctx.datamodel.data}
        lcl['In'] = self.In
        return lcl

    def In(self, expr: str) -> bool:
        """Evaluate condition to determine if transition should occur."""
        match = re.match(
            r'^in\([\'\"](?P<state>.*)[\'\"]\)$',
            expr,
            re.IGNORECASE,
        )
        if match:
            result = match.group('state') in self.ctx.active
        else:
            # TODO: put error on 'error.execution' on internal event
            # queue
            result = False
        return result

    # @singledispatchmethod
    # @abstractmethod
    # def dispatch(
    #     self, expr: 'ExecutableContent', *args: Any, **kwargs: Any
    # ) -> bool:
    #     """Dispatch expression."""

    @singledispatchmethod
    @abstractmethod
    def eval(
        self, expr: Union[Callable, bool, str], *args: Any, **kwargs: Any
    ) -> bool:
        """Evaluate expression."""

    @singledispatchmethod
    @abstractmethod
    def exec(
        self, expr: Union[Callable, str], *args: Any, **kwargs: Any
    ) -> Optional[Any]:
        """Execute expression."""

    def handle(
        self, expr: 'ExecutableContent', *args: Any, **kwargs: Any
    ) -> Optional[Any]:
        """Accept callbacks for executable content."""
        print(expr)
        return expr.callback(self, *args, **kwargs)
