"""Provide common types for statechart components."""

from abc import ABC, abstractmethod  # pylint: disable=no-name-in-module
from typing import (
    Any,
    Callable,
    Iterable,
    Optional,
    Type,
    Union,
)

from superstate.exception import InvalidConfig

EventAction = Union[Callable, str]
EventActions = Union[EventAction, Iterable[EventAction]]
GuardCondition = Union[Callable, str]
GuardConditions = Union[GuardCondition, Iterable[GuardCondition]]
InitialType = Union[Callable, str]


class Validator(ABC):
    """Descriptor validator."""

    name: str

    def __set_name__(self, obj: object, name: str) -> None:
        self.name = name

    def __get__(
        self, obj: object, objtype: Optional[Type[object]] = None
    ) -> str:
        return getattr(obj, f"_{self.name}")

    def __set__(self, obj: object, value: Any) -> None:
        self.validate(value)
        setattr(obj, f"_{self.name}", value)

    @abstractmethod
    def validate(self, value: Any) -> None:
        """Abstract for string validation."""


class Binding(Validator):
    """String descriptor with validation."""

    def __init__(self, *items: str) -> None:
        super().__init__()
        self.__states = items

    def validate(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError(f"Expected {value!r} to be string")
        if value not in self.__states:
            raise ValueError(
                f"Expected {value!r} to be one of {self.__states}"
            )


class NameDescriptor:
    """Validate state naming."""

    # __slots__ = ['id', 'owner']

    def __set_name__(
        self, owner: object, id: str  # pylint: disable=redefined-builtin
    ) -> None:
        self.owner = owner  # pylint: disable=attribute-defined-outside-init
        self.id = id  # pylint: disable=attribute-defined-outside-init

    def __get__(self, obj: object, objtype: Optional[str] = None) -> str:
        return getattr(obj, self.id)

    def __set__(self, obj: object, value: str) -> None:
        if not value.replace('_', '').isalnum():
            raise InvalidConfig('state id contains invalid characters')
        setattr(obj, self.id, value)


class ActionBase(ABC):
    """Base class for actions."""

    @abstractmethod
    def run(self, fn: 'EventAction', *args: Any, **kwargs: Any) -> Any:
        """Run action."""


class GuardBase(ABC):
    """Base class for conditions."""

    @abstractmethod
    def check(self, cond: 'GuardCondition', *args: Any, **kwargs: Any) -> Any:
        """Evaluate condition."""
