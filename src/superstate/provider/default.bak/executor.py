"""Provide common utils for statechart components."""

import inspect
from collections.abc import Callable
from functools import singledispatchmethod
from typing import TYPE_CHECKING, Any, Union

from superstate.exception import InvalidAction  # InvalidConfig
from superstate.provider.base import ExecutorBase

if TYPE_CHECKING:
    from superstate.machine import StateChart


class Executor(ExecutorBase):
    """Provide runutor for action actions."""

    ctx: 'StateChart'

    @singledispatchmethod
    def exec(
        self,
        action: Union[Callable, str],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Evaluate action."""
        raise NotImplementedError(
            'datamodel does not support provided action type'
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
