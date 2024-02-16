"""Provide common utils for statechart components."""

import inspect
from functools import singledispatchmethod
from typing import TYPE_CHECKING, Any, Callable, Tuple  # Union

from superstate.exception import InvalidAction  # InvalidConfig
from superstate.model import Assign, ForEach, Log, Raise
from superstate.provider.base import ExecutorBase

# from superstate.utils import lookup_subclasses

if TYPE_CHECKING:
    from superstate.machine import StateChart
    from superstate.model import Action
    from superstate.types import ExpressionType


class Executor(ExecutorBase):
    """Provide runutor for action expressions."""

    ctx: 'StateChart'

    @singledispatchmethod
    def exec(self, action: 'Action', *args: Any, **kwargs: Any) -> None:
        """Evaluate action."""

    @exec.register
    def _(self, action: Assign) -> None:
        """Evaluate action."""

    @exec.register
    def _(self, action: ForEach) -> None:
        """Evaluate action."""

    @exec.register
    def _(self, action: Log) -> None:
        """Evaluate action."""

    @exec.register
    def _(self, action: Raise) -> None:
        """Evaluate action."""

    def execute(self, expression: str) -> None:
        """Evaluate expression."""
        local = {
            x: (
                getattr(self.ctx, x)
                if callable(x)
                else lambda v, x=x: setattr(self.ctx, x, v)
            )
            for x in dir(self.ctx)
            if not x.startswith('_') and x not in ('ctx', 'run')
        }

        code = compile(expression, '<string>', 'exec')

        for name in code.co_names:
            if name not in local:
                raise NameError(f'Use of {name} not allowed')
        # pylint: disable-next=exec-used
        exec(code, {'__builtins__': {}}, local)

    @staticmethod
    def __run(expression: Callable, *args: Any, **kwargs: Any) -> Any:
        signature = inspect.signature(expression)
        if len(signature.parameters.keys()) != 0:
            return expression(*args, **kwargs)
        return expression()

    def run(
        self,
        expression: 'ExpressionType',
        *args: Any,
        **kwargs: Any,
    ) -> Tuple[Any, ...]:
        """Run expression when transexpression is processed."""
        if callable(expression):
            return self.__run(expression, self.ctx, *args, **kwargs)
        if hasattr(self.ctx, expression):
            return self.__run(getattr(self.ctx, expression), *args, **kwargs)
        raise InvalidAction('could not process action type.')
