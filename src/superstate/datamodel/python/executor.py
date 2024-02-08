"""Provide common utils for statechart components."""

import inspect
from typing import TYPE_CHECKING, Any, Callable, Tuple

from superstate.model.expression.base import ActionBase, ConditionBase

if TYPE_CHECKING:
    from superstate.types import ActionType, ConditionType


class Activity:
    """Long running action."""


class Action(ActionBase):
    """Provide executable action from transition."""

    @staticmethod
    def __run(statement: Callable, *args: Any, **kwargs: Any) -> Any:
        signature = inspect.signature(statement)
        if len(signature.parameters.keys()) != 0:
            return statement(*args, **kwargs)
        return statement()

    def run(
        self,
        statement: 'ActionType',
        *args: Any,
        **kwargs: Any,
    ) -> Tuple[Any, ...]:
        """Run statement when transstatement is processed."""
        if callable(statement):
            return self.__run(statement, self.ctx, *args, **kwargs)
        return self.__run(getattr(self.ctx, statement), *args, **kwargs)


class Condition(ConditionBase):
    """Provide guard condition to determine when transitions should occur."""

    def check(
        self, statement: 'ConditionType', *args: Any, **kwargs: Any
    ) -> bool:
        """Evaluate condition to determine if transition should occur."""
        if callable(statement):
            return statement(self.ctx, *args, **kwargs)
        guard = getattr(self.ctx, statement)
        if callable(guard):
            signature = inspect.signature(guard)
            params = dict(signature.parameters)
            if len(params.keys()) != 0:
                return guard(*args, **kwargs)
            return guard()
        return bool(guard)
