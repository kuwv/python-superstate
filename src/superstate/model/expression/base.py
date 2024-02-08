"""Provide common types for statechart components."""

from abc import ABC, abstractmethod  # pylint: disable=no-name-in-module
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from superstate.machine import StateChart
    from superstate.types import ActionType, ConditionType

T = TypeVar('T')


class ActionBase(ABC):
    """Base class for actions."""

    def __init__(self, ctx: 'StateChart') -> None:
        """Initialize for MyPy."""
        self.__ctx = ctx

    @property
    def ctx(self) -> 'StateChart':
        """Return instance of StateChart."""
        return self.__ctx

    @abstractmethod
    def run(self, statement: 'ActionType', *args: Any, **kwargs: Any) -> Any:
        """Run action."""


class ConditionBase(ABC):
    """Base class for conditions."""

    def __init__(self, ctx: 'StateChart') -> None:
        """Initialize for MyPy."""
        self.__ctx = ctx

    @property
    def ctx(self) -> 'StateChart':
        """Return instance of StateChart."""
        return self.__ctx

    @abstractmethod
    def check(
        self, statement: 'ConditionType', *args: Any, **kwargs: Any
    ) -> bool:
        """Evaluate condition."""
