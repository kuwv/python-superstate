"""Provide common types for statechart components."""

import inspect
from collections.abc import Callable
from functools import singledispatchmethod
from typing import Any, Union

from superstate.exception import InvalidAction  # InvalidConfig
from superstate.model import Action, Assign, ElseIf, If
from superstate.provider.base import Provider


class Default(Provider):
    """Default data model providing state data."""

    # TODO: pull config from system settings within DataModel to configure
    # layout

    # @property
    # def dispatcher(self) -> Type['DispatcherBase']:
    #     """Get the configured dispath expression language."""

    @singledispatchmethod
    def eval(
        self,
        action: Union[Action, Callable, str],
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        raise NotImplementedError(
            'datamodel cannot evaluate provided action type'
        )

    @eval.register
    def _(self, action: Union[If, ElseIf]) -> bool:
        """Evaluate condition to determine if transition should occur."""
        allowed = {
            x: getattr(self.ctx, x)
            for x in dir(self.ctx)
            if not x.startswith('_') and x not in ('ctx', 'eval')
        }

        code = compile(action.cond, '<string>', 'eval')

        for name in code.co_names:
            if name not in allowed:
                raise NameError(f'Use of {name} not allowed')
        # pylint: disable-next=eval-used
        return eval(code, {'__builtins__': {}}, allowed)

    @eval.register
    def _(self, action: Callable, *args: Any, **kwargs: Any) -> bool:
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

    @singledispatchmethod
    def exec(
        self,
        action: Union[Action, Callable, str],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Evaluate action."""
        raise NotImplementedError(
            'datamodel cannot execute provided action type'
        )

    @staticmethod
    def __exec(action: Callable, *args: Any, **kwargs: Any) -> Any:
        signature = inspect.signature(action)
        if len(signature.parameters.keys()) != 0:
            return action(*args, **kwargs)
        return action()

    @exec.register
    def _(
        self,
        action: Assign,
        # *args: Any,
        # **kwargs: Any,
    ) -> Any:
        """Run action when transaction is processed."""
        if action.expr is not None and type(action.expr) in dir(__builtins__):
            local = {
                x: (
                    getattr(self.ctx, x)
                    if callable(x)
                    else lambda v, x=x: setattr(self.ctx, x, v)
                )
                for x in dir(self.ctx)
                if not x.startswith('_') and x not in ('ctx', 'run')
            }

            code = compile(action.expr, '<string>', 'exec')

            for name in code.co_names:
                if name not in local:
                    raise NameError(f'Use of {name} not allowed')
            # pylint: disable-next=exec-used
            exec(code, {'__builtins__': {}}, local)
        else:
            self.ctx[action.location] = action.expr

    @exec.register
    def _(
        self,
        action: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Run action when transaction is processed."""
        return self.__exec(action, self.ctx, *args, **kwargs)

    @exec.register
    def _(
        self,
        action: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if hasattr(self.ctx, action):
            return self.__exec(getattr(self.ctx, action), *args, **kwargs)
        raise InvalidAction('could not process action type.')
