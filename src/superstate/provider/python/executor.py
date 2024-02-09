"""Provide common utils for statechart components."""

import inspect
from typing import TYPE_CHECKING, Any, Callable, Tuple, Union

from superstate.exception import InvalidAction, InvalidConfig
from superstate.model.expression.base import ActionBase

# from superstate.utils import lookup_subclasses

if TYPE_CHECKING:
    from superstate.machine import StateChart


class Activity:
    """Long running action."""


class Action(ActionBase):
    """Provide executable action from transition."""

    # pylint: disable-next=unused-argument
    # def __new__(cls, *args: Any, **kwargs: Any) -> 'Action':
    #     """Return action type."""
    #     if 'assign' in args:
    #         pass
    #     if 'if' in args:
    #         pass
    #     if 'elseif' in args:
    #         pass
    #     if 'else' in args:
    #         pass
    #     if 'foreach' in args:
    #         pass
    #     if 'log' in args:
    #         pass
    #     if 'raise' in args:
    #         pass

    #     # for subclass in lookup_subclasses(cls):
    #     #     if subclass.__name__.lower().startswith(kind):
    #     #         return super().__new__(subclass)
    #     return super().__new__(cls)

    # @classmethod
    # def create(cls, settings: Union['Action', dict]) -> 'Action':
    #     """Create state from configuration."""
    #     if isinstance(settings, Action):
    #         return settings
    #     if isinstance(settings, dict):
    #         print(settings)
    #         return cls(**settings)
    #     raise InvalidConfig('could not find a valid transition configuration')

    @staticmethod
    def __run(statement: Callable, *args: Any, **kwargs: Any) -> Any:
        signature = inspect.signature(statement)
        if len(signature.parameters.keys()) != 0:
            return statement(*args, **kwargs)
        return statement()

    def run(
        self,
        ctx: 'StateChart',
        *args: Any,
        **kwargs: Any,
    ) -> Tuple[Any, ...]:
        """Run statement when transstatement is processed."""
        if callable(self.statement):
            return self.__run(self.statement, ctx, *args, **kwargs)
        if hasattr(ctx, self.statement):
            return self.__run(getattr(ctx, self.statement), *args, **kwargs)
        raise InvalidAction('could not process action of transition.')
