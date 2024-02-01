"""Provide common types for statechart components."""

import re
from abc import ABC, abstractmethod  # pylint: disable=no-name-in-module
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

from superstate.exception import InvalidConfig

if TYPE_CHECKING:
    from superstate.machine import StateChart

EventAction = Union[Callable, str]
EventActions = Union[EventAction, Sequence[EventAction]]
GuardCondition = Union[Callable, str]
GuardConditions = Union[GuardCondition, Sequence[GuardCondition]]
Initial = Union[Callable, str]

T = TypeVar('T')


class Validator(ABC):
    """Descriptor validator."""

    name: str

    def __set_name__(self, obj: object, name: str) -> None:
        self.name = name

    def __get__(self, obj: object, objtype: Optional[Type[T]] = None) -> T:
        return getattr(obj, f"_{self.name}")

    def __set__(self, obj: object, value: T) -> None:
        self.validate(value)
        setattr(obj, f"_{self.name}", value)

    @abstractmethod
    def validate(self, value: Any) -> None:
        """Abstract for string validation."""


class Selection(Validator):
    """String descriptor with validation."""

    def __init__(self, *items: str) -> None:
        super().__init__()
        self.__items = items

    def validate(self, value: T) -> None:
        if not isinstance(value, str):
            raise ValueError(f"Expected {value!r} to be string")
        if value not in self.__items:
            raise ValueError(f"Expected {value!r} to be one of {self.__items}")


class Identifier(Validator):
    """Validate state naming."""

    def __init__(self, pattern: str = r'^[a-zA-Z][a-zA-Z0-9:\.\-_]*$') -> None:
        super().__init__()
        self.pattern = pattern

    def validate(self, value: str) -> None:
        print(value)
        match = re.match(self.pattern, value, re.IGNORECASE)
        if not match:
            raise InvalidConfig('provided identifier is invalid')


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
    def run(self, cmd: 'EventAction', *args: Any, **kwargs: Any) -> Any:
        """Run action."""


class GuardBase(ABC):
    """Base class for conditions."""

    def __init__(self, ctx: 'StateChart') -> None:
        """Initialize for MyPy."""
        self.__ctx = ctx

    @property
    def ctx(self) -> 'StateChart':
        """Return instance of StateChart."""
        return self.__ctx

    @abstractmethod
    def check(self, cond: 'GuardCondition', *args: Any, **kwargs: Any) -> bool:
        """Evaluate condition."""
