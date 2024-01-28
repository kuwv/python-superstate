"""Provide common utils for statechart components."""

import inspect
from typing import TYPE_CHECKING, Any, Callable, Tuple

from superstate.types import ActionBase, GuardBase

if TYPE_CHECKING:
    from superstate.types import EventAction, GuardCondition


def tuplize(value: Any) -> Tuple[Any, ...]:
    """Convert various collection types to tuple."""
    return tuple(value) if type(value) in (list, tuple) else (value,)


class Activity:
    """Long running action."""


class Action(ActionBase):
    """Provide executable action from transition."""

    __slots__ = ['__ctx']

    def run(
        self,
        cmd: 'EventAction',
        *args: Any,
        **kwargs: Any,
    ) -> Tuple[Any, ...]:
        """Run action when transaction is processed."""
        if callable(cmd):
            return self.__run(cmd, self.ctx, *args, **kwargs)
        return self.__run(getattr(self.ctx, cmd), *args, **kwargs)

    @staticmethod
    def __run(action: Callable, *args: Any, **kwargs: Any) -> Any:
        signature = inspect.signature(action)
        if len(signature.parameters.keys()) != 0:
            return action(*args, **kwargs)
        return action()


class Guard(GuardBase):
    """Provide guard condition to determine when transitions should occur."""

    __slots__ = ['__ctx']

    def check(self, cond: 'GuardCondition', *args: Any, **kwargs: Any) -> bool:
        """Evaluate condition to determine if transition should occur."""
        if callable(cond):
            return cond(self.ctx, *args, **kwargs)
        guard = getattr(self.ctx, cond)
        if callable(guard):
            signature = inspect.signature(guard)
            params = dict(signature.parameters)
            if len(params.keys()) != 0:
                return guard(*args, **kwargs)
            return guard()
        return bool(guard)
