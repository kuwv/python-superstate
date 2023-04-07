"""Provide common utils for statechart components."""

import inspect
from typing import TYPE_CHECKING, Any, Callable, Tuple

if TYPE_CHECKING:
    from superstate.machine import StateChart
    from superstate.types import (
        EventAction,
        EventActions,
        GuardCondition,
        GuardConditions,
    )


def tuplize(value: Any) -> Tuple[Any, ...]:
    """Convert various collection types to tuple."""
    return tuple(value) if type(value) in (list, tuple) else (value,)


class Activity:
    """Long running action."""


class Action:
    """Provide executable action from transition."""

    __slots__ = ['__machine']

    def __init__(self, machine: 'StateChart') -> None:
        self.__machine = machine

    def run(
        self,
        params: 'EventActions',
        *args: Any,
        **kwargs: Any,
    ) -> Tuple[Any, ...]:
        """Run action when transaction is processed."""
        return tuple(
            self.__run_action(x, *args, **kwargs) for x in tuplize(params)
        )

    def __run_action(
        self, action: 'EventAction', *args: Any, **kwargs: Any
    ) -> Any:
        if callable(action):
            return self.__run_with_args(
                action, self.__machine, *args, **kwargs
            )
        return self.__run_with_args(
            getattr(self.__machine, action), *args, **kwargs
        )

    @staticmethod
    def __run_with_args(action: Callable, *args: Any, **kwargs: Any) -> Any:
        signature = inspect.signature(action)
        if len(signature.parameters.keys()) != 0:
            return action(*args, **kwargs)
        return action()


class Guard:
    """Provide guard condition to determine when transitions should occur."""

    __slots__ = ['__machine']

    def __init__(self, machine: 'StateChart') -> None:
        self.__machine = machine

    def evaluate(
        self, cond: 'GuardConditions', *args: Any, **kwargs: Any
    ) -> bool:
        """Evaluate condition to determine if transition should occur."""
        result = True
        for _cond in tuplize(cond):
            result = result and self.__evaluate(_cond, *args, **kwargs)
            if result is False:
                break
        return result

    def __evaluate(
        self, cond: 'GuardCondition', *args: Any, **kwargs: Any
    ) -> bool:
        if callable(cond):
            return cond(self.__machine, *args, **kwargs)
        guard = getattr(self.__machine, cond)
        if callable(guard):
            return self.__evaluate_with_args(guard, *args, **kwargs)
        return bool(guard)

    @staticmethod
    def __evaluate_with_args(
        cond: Callable, *args: Any, **kwargs: Any
    ) -> bool:
        signature = inspect.signature(cond)
        params = dict(signature.parameters)
        if len(params.keys()) != 0:
            return cond(*args, **kwargs)
        return cond()
