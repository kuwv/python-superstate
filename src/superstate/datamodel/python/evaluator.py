"""Provide common utils for statechart components."""

import inspect
from typing import TYPE_CHECKING, Any

from superstate.model.expression.base import ConditionBase

if TYPE_CHECKING:
    from superstate.types import ConditionType


class Condition(ConditionBase):
    """Provide guard condition to determine when transitions should occur."""

    def check(self, cond: 'ConditionType', *args: Any, **kwargs: Any) -> bool:
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
