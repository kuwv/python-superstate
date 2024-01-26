"""Provide Null Data Model."""

import re
from typing import TYPE_CHECKING, Any

from superstate.types import GuardBase

if TYPE_CHECKING:
    from superstate.machine import StateChart
    from superstate.types import GuardCondition


class In(GuardBase):
    """Provide condition using 'in' predicate to determine transition."""

    __slots__ = ['__ctx']

    def __init__(self, ctx: 'StateChart') -> None:
        super().__init__()
        self.__ctx = ctx

    def check(self, cond: 'GuardCondition', *args: Any, **kwargs: Any) -> bool:
        """Evaluate condition to determine if transition should occur."""
        if isinstance(cond, str):
            match = re.match(
                r'^in\([\'\"](?P<state>.*)[\'\"]\)$', cond, re.IGNORECASE
            )
            if match:
                result = match.group('state') in self.__ctx.active
            else:
                # TODO: put error on 'error.execution' on internal event queue
                result = False
            return result
        raise Exception('incorrect condition provided to In() expression.')
