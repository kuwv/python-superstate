"""Provide common utils for statechart components."""

from functools import singledispatchmethod
from typing import TYPE_CHECKING, Any, Union

from superstate.model import If, ElseIf  # Else
from superstate.provider.base import EvaluatorBase

if TYPE_CHECKING:
    from superstate.machine import StateChart
    from superstate.model import Action


class Evaluator(EvaluatorBase):
    """Provide guard condition to determine when transitions should occur."""

    ctx: 'StateChart'

    @singledispatchmethod
    def eval(self, action: 'Action', *args: Any, **kwargs: Any) -> bool:
        raise NotImplementedError('eval not implemented.')

    @eval.register
    def _(self, action: str) -> bool:
        """Evaluate action."""
        allowed = {
            x: getattr(self.ctx, x)
            for x in dir(self.ctx)
            if not x.startswith('_') and x not in ('ctx', 'eval')
        }

        code = compile(action, '<string>', 'eval')

        for name in code.co_names:
            if name not in allowed:
                raise NameError(f'Use of {name} not allowed')
        # pylint: disable-next=eval-used
        return eval(code, {'__builtins__': {}}, allowed)

    @eval.register
    def _(self, action: Union[If, ElseIf]) -> bool:
        """Evaluate action."""
        return self.eval(action.cond)

    # @eval.register
    # def _(self, action: Else) -> bool:
    #     """Evaluate action."""
    #     return True
