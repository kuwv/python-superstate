"""Provide common types for statechart components."""

from typing import Callable, Iterable, Union

EventAction = Union[Callable, str]
EventActions = Union[EventAction, Iterable[EventAction]]
GuardCondition = Union[Callable, str]
GuardConditions = Union[GuardCondition, Iterable[GuardCondition]]
InitialType = Union[Callable, str]
