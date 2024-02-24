"""Provide common types for statechart components."""

import inspect
from collections.abc import Callable
from functools import singledispatchmethod
from typing import Any, Union

from superstate.exception import InvalidAction  # InvalidConfig
from superstate.model import (
    # Action,
    Assign,
    Conditional,
    # ElseIf,
    # If,
    Script,
)
from superstate.provider.base import Provider


class Default(Provider):
    """Default data model providing state data."""

    # TODO: pull config from system settings within DataModel to configure
    # layout

    # @singledispatchmethod
    # def dispatch(self) -> Type['DispatcherBase']:
    #     """Get the configured dispath expression language."""

    @singledispatchmethod
    def eval(
        self,
        action: Union[Callable, str],
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        raise NotImplementedError(
            'datamodel cannot evaluate provided action type',
            type(action),
            action,
        )

    @eval.register
    def _(self, action: bool) -> bool:
        """Evaluate condition to determine if transition should occur."""
        # print('--eval call--', action)
        return action

    @eval.register
    def _(self, action: Callable, *args: Any, **kwargs: Any) -> bool:
        """Evaluate condition to determine if transition should occur."""
        # print('--eval call--', action)
        return action(self.ctx, *args, **kwargs)

    @eval.register
    def _(self, action: str, *args: Any, **kwargs: Any) -> bool:
        """Evaluate condition to determine if transition should occur."""
        # print('--eval str--', action)
        guard = getattr(self.ctx, action)
        if callable(guard):
            signature = inspect.signature(guard)
            params = dict(signature.parameters)
            if len(params.keys()) != 0:
                return guard(*args, **kwargs)
            return guard()
        return bool(guard)

    # @eval.register
    # def _(self, action: Union[If, ElseIf]) -> bool:
    #     """Evaluate condition to determine if transition should occur."""
    #     code = compile(action.cond, '<string>', 'eval')
    #     for name in code.co_names:
    #         if name not in allowed:
    #             raise NameError(f'Use of {name} not allowed')
    #     # pylint: disable-next=eval-used
    #     return eval(code, self.globals, self.locals)

    @singledispatchmethod
    def exec(
        self,
        action: Union[Script, str],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Evaluate action."""
        raise NotImplementedError(
            'datamodel cannot execute provided action type', type(action)
        )

    @staticmethod
    def __exec(action: Callable, *args: Any, **kwargs: Any) -> Any:
        signature = inspect.signature(action)
        if len(signature.parameters.keys()) != 0:
            return action(*args, **kwargs)
        return action()

    @exec.register
    def _(self, action: Assign) -> None:
        """Run action when transaction is processed."""
        setattr(self.ctx, action.location, action)

    @exec.register
    def _(
        self,
        action: Script,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Run action when transaction is processed."""
        # print('--exec script--', action)
        if callable(action.src):
            return self.__exec(action.src, self.ctx, *args, **kwargs)
        return self.exec(action.src, *args, **kwargs)

    @exec.register
    def _(
        self,
        action: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Run action when transaction is processed."""
        # print('--exec str--', action)
        if hasattr(self.ctx, action):
            return self.__exec(getattr(self.ctx, action), *args, **kwargs)
        raise InvalidAction('could not process action type.')

    # @exec.register
    # def _(
    #     self,
    #     action: str,
    #     # *args: Any,
    #     # **kwargs: Any,
    # ) -> Optional[Any]:
    #     """Run action when transaction is processed."""
    #     if action is not None and type(action) in dir(__builtins__):
    #         code = compile(action, '<string>', 'exec')
    #         for name in code.co_names:
    #             if name not in local:
    #                 raise NameError(f'Use of {name} not allowed')
    #         # pylint: disable-next=exec-used
    #         return exec(code, self.globals, self.locals)
    #     return self.ctx[action.location] = action
