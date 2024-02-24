"""Provide common types for statechart components."""

# import re
from abc import ABC, abstractmethod  # pylint: disable=no-name-in-module
from functools import singledispatchmethod
from typing import TYPE_CHECKING, Any, Dict, Optional, Type, TypeVar

from superstate.exception import InvalidConfig
from superstate.utils import lookup_subclasses

if TYPE_CHECKING:
    from superstate.machine import StateChart
    from superstate.model.base import Action

T = TypeVar('T')


# class In:
#     """Provide condition using 'In()' predicate to determine transition."""
#
#     @classmethod
#     def eval(cls, action: 'Action') -> bool:
#         """Evaluate condition to determine if transition should occur."""
#         if isinstance(action, str):
#             match = re.match(
#                 r'^in\([\'\"](?P<state>.*)[\'\"]\)$',
#                 action,
#                 re.IGNORECASE,
#             )
#             if match:
#                 result = match.group('state') in self.ctx.active
#             else:
#                 # TODO: put error on 'error.execution' on internal event
#                 # queue
#                 result = False
#             return result
#         raise InvalidConfig(
#             'incorrect condition provided to In() expression.'
#         )


class Provider(ABC):
    """Instantiate state types from class metadata."""

    enabled: str = 'default'
    # should support platform-specific, global, and local variables

    def __init__(self, ctx: 'StateChart') -> None:
        """Initialize for MyPy."""
        self.__ctx = ctx

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
    def ctx(self) -> 'StateChart':
        """Return instance of StateChart."""
        return self.__ctx

    @property
    def locals(self) -> Dict[str, Any]:
        """Get local attributes and methods available for eval and exec."""
        return {
            x: (
                getattr(self.ctx, x)
                if callable(x)
                else lambda v, x=x: setattr(self.ctx, x, v)
            )
            for x in dir(self.ctx)
            if not x.startswith('_') and x not in ('ctx', 'run')
        }

    @property
    def globals(self) -> Dict[str, Any]:
        """Get global attributes and methods available for eval and exec."""
        return {'__builtins__': {}}

    # @singledispatchmethod
    # @abstractmethod
    # def dispatch(self, action: 'Action', *args: Any, **kwargs: Any) -> bool:
    #     """Dispatch action."""

    @singledispatchmethod
    @abstractmethod
    def eval(self, action: 'Action', *args: Any, **kwargs: Any) -> bool:
        """Evaluate action."""

    @singledispatchmethod
    @abstractmethod
    def exec(
        self, action: 'Action', *args: Any, **kwargs: Any
    ) -> Optional[Any]:
        """Execute action."""

    def run(self, action: 'Action') -> None:
        """Accept action callbacks."""
        action.callback(self)
