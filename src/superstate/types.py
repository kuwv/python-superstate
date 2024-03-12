"""Provide common types for statechart components."""

import re
from abc import ABC, abstractmethod  # pylint: disable=no-name-in-module
from collections.abc import Callable
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

from superstate.exception import InvalidConfig

if TYPE_CHECKING:
    from superstate.model import Action

ExpressionType = Union[Callable, str]
ExpressionTypes = Sequence['ExpressionType']
ActionTypes = Sequence['Action']
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

    # TODO: consider dynamic enum instead
    def __init__(self, *allowed: str) -> None:
        super().__init__()
        self.allowed = allowed

    def validate(self, value: T) -> None:
        if not isinstance(value, str):
            raise ValueError(f"Expected {value!r} to be string")
        if value not in self.allowed:
            raise ValueError(f"Expected {value!r} to be one of {self.allowed}")


class Identifier(Validator):
    """Validate state naming."""

    def __init__(self, pattern: str = r'^[a-zA-Z][a-zA-Z0-9:\.\-_]*$') -> None:
        super().__init__()
        self.pattern = pattern

    def validate(self, value: str) -> None:
        match = re.match(self.pattern, value, re.IGNORECASE)
        if not match:
            raise InvalidConfig('provided identifier is invalid')


class Expression(Validator):
    """Validate valueession."""

    def validate(self, value: 'ExpressionType') -> None:
        """Validate valueession."""
        if isinstance(value, str):
            if '\n' in value:
                raise InvalidConfig('expressions cannot contian newline')
            if ';' in value:
                raise InvalidConfig('expressions cannot be chained')


class Final(Generic[T]):
    """Provide final attribute descriptor."""

    def __init__(self, value: Optional[T] = None) -> None:
        """Initialize default value for attribute."""
        self.value = value

    def __get__(self, obj: object, objtype: Type[T]) -> Optional[T]:
        return self.value

    def __set__(self, obj: object, value: T) -> None:
        if self.value is None:
            self.value = value
