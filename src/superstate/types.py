"""Provide common types for statechart components."""

from typing import Callable, Iterable, Optional, Union

from superstate.exception import InvalidConfig
from superstate.state import CompoundState, ParallelState

CompositeState = Union[CompoundState, ParallelState]
EventAction = Union[Callable, str]
EventActions = Union[EventAction, Iterable[EventAction]]
GuardCondition = Union[Callable, str]
GuardConditions = Union[GuardCondition, Iterable[GuardCondition]]
InitialType = Union[Callable, str]


class NameDescriptor:
    """Validate state naming."""

    __slots__ = ['__name']

    def __init__(self, name: str) -> None:
        self.__name = name

    def __get__(self, key: str, objtype: Optional[str] = None) -> str:
        return getattr(key, self.__name)

    def __set__(self, key: str, value: str) -> None:
        if not value.replace('_', '').isalnum():
            raise InvalidConfig('state name contains invalid characters')
        setattr(key, self.__name, value)
