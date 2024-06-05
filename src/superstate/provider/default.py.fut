"""Provide common types for statechart components."""

import inspect
from collections.abc import Callable
from functools import singledispatchmethod
from typing import Any, Dict, Union

from RestrictedPython import (
    compile_restricted,
    safe_builtins,
    limited_builtins,
    utility_builtins,
)
from RestrictedPython.Eval import (
    default_guarded_getattr,
    default_guarded_getiter,
    default_guarded_getitem,
)
from RestrictedPython.Guards import (
    full_write_guard,
    guarded_iter_unpack_sequence,
)

# from superstate.exception import InvalidAction  # InvalidConfig

# from superstate.model import (
#     # Action,
#     Assign,
#     Conditional,
#     # ElseIf,
#     # If,
#     Script,
# )
from superstate.provider.base import Provider


class Default(Provider):
    """Default data model providing state data."""

    # TODO: pull config from system settings within DataModel to configure
    # layout

    # @singledispatchmethod
    # def dispatch(self) -> Type['DispatcherBase']:
    #     """Get the configured dispath expression language."""

    @property
    def globals(self) -> Dict[str, Any]:
        """Provide globals for processing expr."""
        return {
            '__builtins__': safe_builtins,
            # '__name__': 'prototype',
            '__metaclass__': type,
            '_getattr_': default_guarded_getattr,
            '_getitem_': default_guarded_getitem,
            '_getiter_': default_guarded_getiter,
            '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
            '_write_': full_write_guard,
            **limited_builtins,
            **utility_builtins,
        }

    @property
    def locals(self) -> Dict[str, Any]:
        """Provide locals for processing expressions."""
        return {
            x: getattr(self.ctx, x)
            for x in dir(self.ctx)
            if not x.startswith('__')
        }

    @singledispatchmethod
    def eval(
        self,
        expr: Union[Callable, bool, str],
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        raise NotImplementedError(
            'datamodel cannot evaluate provided expr type', expr
        )

    @eval.register
    def _(self, expr: bool) -> bool:
        """Evaluate condition to determine if transition should occur."""
        return expr

    @eval.register
    def _(self, expr: Callable, *args: Any, **kwargs: Any) -> bool:
        """Evaluate condition to determine if transition should occur."""
        return expr(self.ctx, *args, **kwargs)

    @eval.register
    def _(self, expr: str) -> bool:
        """Call compile_restricted_eval and actually eval it."""
        code = compile_restricted(expr, '<string>', 'eval')
        # pylint: disable-next=eval-used
        return eval(code, self.globals, self.locals)

    @singledispatchmethod
    def exec(
        self,
        expr: Union[Callable, str],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Evaluate expr."""
        raise NotImplementedError(
            'datamodel cannot execute provided expression type', type(expr)
        )

    @exec.register
    def _(self, expr: Callable, *args: Any, **kwargs: Any) -> Any:
        signature = inspect.signature(expr)
        if len(signature.parameters.keys()) != 0:
            return expr(self.ctx, *args, **kwargs)
        if len(signature.parameters.keys()) == 1:
            return expr(self.ctx)
        return expr()

    @exec.register
    def _(
        self,
        expr: str,
        # *args: Any,
        # **kwargs: Any,
    ) -> Any:
        for k, v in self.locals.items():
            print(k, v)
        code = compile(expr, '<string>', 'exec')
        # code = compile_restricted(expr, '<string>', 'exec')
        values = self.locals.copy()
        # pylint: disable-next=exec-used
        exec(code, self.globals, values)
        self.ctx.__dict__.update(
            {k: v for k, v in values.items() if not callable(v)}
        )
        return self.ctx
