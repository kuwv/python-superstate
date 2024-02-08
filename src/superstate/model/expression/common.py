"""Provide common expressions used by all data models."""

import re
from typing import TYPE_CHECKING, Any

from superstate.model.expression.base import ConditionBase

if TYPE_CHECKING:
    from superstate.types import ConditionType


class In(ConditionBase):
    """Provide condition using 'in()' predicate to determine transition."""

    def check(self, cond: 'ConditionType', *args: Any, **kwargs: Any) -> bool:
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
