"""Provide common types for statechart components."""

import inspect
from collections.abc import Callable
from functools import singledispatchmethod
from typing import Any, Union

from superstate.exception import InvalidAction  # InvalidConfig
from superstate.provider.base import Provider


class Default(Provider):
    """Default data model providing state data."""

    # TODO: pull config from system settings within DataModel to configure
    # layout

    # @singledispatchmethod
    # def dispatch(self) -> Type['DispatcherBase']:
    #     """Get the configured dispath expression language."""

    @staticmethod
    def __call(expr: Callable, *args: Any, **kwargs: Any) -> Any:
        # print(expr, args, kwargs)
        signature = inspect.signature(expr)
        if len(signature.parameters.keys()) != 0:
            return expr(*args, **kwargs)
        return expr()

    @singledispatchmethod
    def eval(
        self,
        expr: Union[Callable, bool, str],
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        raise NotImplementedError(
            'datamodel cannot evaluate provided expression type', expr
        )

    @eval.register
    def _(self, expr: bool) -> bool:
        """Evaluate condition to determine if transition should occur."""
        # print('--eval call--', expr)
        return expr

    @eval.register
    def _(self, expr: Callable, *args: Any, **kwargs: Any) -> bool:
        """Evaluate condition to determine if transition should occur."""
        # print('--eval call--', expr)
        return expr(self.ctx, *args, **kwargs)

    @eval.register
    def _(self, expr: str, *args: Any, **kwargs: Any) -> bool:
        """Evaluate condition to determine if transition should occur."""
        # print('--eval str--', expr, hasattr(self.ctx, expr))
        if hasattr(self.ctx, expr):
            guard = getattr(self.ctx, expr)
            if callable(guard):
                return self.__call(guard, *args, **kwargs)
            return bool(guard)
        code = compile(expr, '<string>', 'eval')
        # pylint: disable-next=eval-used
        return eval(code, self.globals, self.locals)

    @singledispatchmethod
    def exec(
        self,
        expr: Union[Callable, str],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Evaluate expr."""
        raise NotImplementedError(
            'datamodel cannot execute provided expression type', expr
        )

    @exec.register
    def _(
        self,
        expr: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Run expression when transexpr is processed."""
        # print('--exec script--', expr)
        return self.__call(expr, self.ctx, *args, **kwargs)

    @exec.register
    def _(
        self,
        expr: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Run expression when transexpr is processed."""
        # print('--exec str--', expr)
        if hasattr(self.ctx, expr):
            return self.__call(getattr(self.ctx, expr), *args, **kwargs)
        values = self.locals.copy()
        code = compile(expr, '<string>', 'exec')
        # pylint: disable-next=exec-used
        exec(code, self.globals, values)
        return values
