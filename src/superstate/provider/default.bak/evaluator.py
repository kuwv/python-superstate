"""Provide common utils for statechart components."""

import inspect
from collections.abc import Callable
from functools import singledispatchmethod
from typing import TYPE_CHECKING, Any, Union

from superstate.provider.base import EvaluatorBase

if TYPE_CHECKING:
    from superstate.machine import StateChart


class Evaluator(EvaluatorBase):
    """Provide guard condition to determine when transitions should occur."""

    ctx: 'StateChart'

    @singledispatchmethod
    def eval(
        self, action: Union['Callable', str], *args: Any, **kwargs: Any
    ) -> bool:
        raise NotImplementedError(
            'datamodel does not support provided action type'
        )

    @eval.register
    def _(self, action: 'Callable', *args: Any, **kwargs: Any) -> bool:
        """Evaluate condition to determine if transition should occur."""
        return action(self.ctx, *args, **kwargs)

    @eval.register
    def _(self, action: str, *args: Any, **kwargs: Any) -> bool:
        """Evaluate condition to determine if transition should occur."""
        guard = getattr(self.ctx, action)
        if callable(guard):
            signature = inspect.signature(guard)
            params = dict(signature.parameters)
            if len(params.keys()) != 0:
                return guard(*args, **kwargs)
            return guard()
        return bool(guard)
