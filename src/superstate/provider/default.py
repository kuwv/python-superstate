"""Provide common types for statechart components."""

import inspect
from collections.abc import Callable
from functools import singledispatchmethod
from typing import Any, Union

# from superstate.exception import InvalidAction  # InvalidConfig
from superstate.provider.base import Provider
from superstate.utils import to_bool


class Default(Provider):
    """Default data model providing state data."""

    # TODO: pull config from system settings within DataModel to configure
    # layout

    # @singledispatchmethod
    # def dispatch(self) -> Type['DispatcherBase']:
    #     """Get the configured dispath expression language."""

    @staticmethod
    def __handle(expr: Callable, *args: Any, **kwargs: Any) -> Any:
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
        """Evaluate expression to determine if action should occur."""
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
                return self.__handle(guard, *args, **kwargs)
            return to_bool(guard)
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
        kwargs.pop('_mode_', 'single')
        return self.__handle(expr, self.ctx, *args, **kwargs)

    @exec.register
    def _(
        self,
        expr: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Run expression when transexpr is processed."""
        # print('--exec str--', expr)
        mode = kwargs.pop('_mode_', 'single')
        if hasattr(self.ctx, expr):
            return self.__handle(getattr(self.ctx, expr), *args, **kwargs)
        values = self.locals.copy()
        values['__result__'] = None
        code = compile(f"result = {expr}", '<string>', mode)
        # pylint: disable-next=exec-used
        exec(code, self.globals, values)
        return values['__result__']
