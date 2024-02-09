"""Provide common utils for statechart components."""

import inspect
from typing import TYPE_CHECKING, Any

from superstate.model.expression.base import ConditionBase

if TYPE_CHECKING:
    from superstate.machine import StateChart


class Condition(ConditionBase):
    """Provide guard condition to determine when transitions should occur."""

    def check(self, ctx: 'StateChart', *args: Any, **kwargs: Any) -> bool:
        """Evaluate condition to determine if transition should occur."""
        if callable(self.statement):
            return self.statement(ctx, *args, **kwargs)
        guard = getattr(ctx, self.statement)
        if callable(guard):
            signature = inspect.signature(guard)
            params = dict(signature.parameters)
            if len(params.keys()) != 0:
                return guard(*args, **kwargs)
            return guard()
        return bool(guard)
