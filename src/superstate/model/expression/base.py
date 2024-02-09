"""Provide common types for statechart components."""

from abc import ABC, abstractmethod  # pylint: disable=no-name-in-module
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from superstate.machine import StateChart
    from superstate.types import ActionType, ConditionType

T = TypeVar('T')


class ActionBase(ABC):
    """Base class for actions."""

    # def __init__(
    #     self, settings: Optional[dict] = None, /, **kwargs: Any
    # ) -> None:
    def __init__(self, statement: 'ActionType') -> None:
        """Initialize for MyPy."""
        self.__statement = statement

    # @property
    # def parent(self) -> Optional['CompositeState']:
    #     """Get parent state."""
    #     return self.__parent

    # @parent.setter
    # def parent(self, state: 'CompositeState') -> None:
    #     if self.__parent is None:
    #         self.__parent = state
    #     else:
    #         raise Exception('cannot change parent for state')

    @property
    def statement(self) -> 'ActionType':
        """Return action statement."""
        return self.__statement

    @abstractmethod
    def run(self, ctx: 'StateChart', *args: Any, **kwargs: Any) -> Any:
        """Run action."""


class ConditionBase(ABC):
    """Base class for conditions."""

    def __init__(self, statement: 'ConditionType') -> None:
        """Initialize for MyPy."""
        self.__statement = statement

    @property
    def statement(self) -> 'ConditionType':
        """Return condition statement."""
        return self.__statement

    @abstractmethod
    def check(self, ctx: 'StateChart', *args: Any, **kwargs: Any) -> bool:
        """Evaluate condition."""
