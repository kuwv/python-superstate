"""Provide common types for statechart components."""

import re
from abc import ABC, abstractmethod  # pylint: disable=no-name-in-module
from dataclasses import dataclass
from functools import singledispatchmethod
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Optional,
    Type,
    TypeVar,
    Union,
)

from superstate.exception import InvalidConfig

from superstate.utils import lookup_subclasses

if TYPE_CHECKING:
    from superstate.machine import StateChart
    from superstate.model.base import Action

    # from superstate.provider.base import ExecutorBase

T = TypeVar('T')


class Content(ABC):
    """Base class for content management within eval/exec objects."""

    def __init__(self, ctx: 'StateChart') -> None:
        """Initialize for MyPy."""
        self.__ctx = ctx

    @property
    def ctx(self) -> 'StateChart':
        """Return instance of StateChart."""
        return self.__ctx


class EvaluatorBase(Content):
    """Base class for executing actions."""

    @singledispatchmethod
    @abstractmethod
    def eval(self, action: 'Action', *args: Any, **kwargs: Any) -> bool:
        """Evaluate action."""


class ExecutorBase(Content):
    """Base class for executing actions."""

    @singledispatchmethod
    @abstractmethod
    def exec(self, action: 'Action', *args: Any, **kwargs: Any) -> None:
        """Evaluate action."""


class In:
    """Provide condition using 'In()' predicate to determine transition."""

    def eval(self, action: 'Action', *args: Any, **kwargs: Any) -> bool:
        """Evaluate condition to determine if transition should occur."""
        if isinstance(action, str):
            match = re.match(
                r'^in\([\'\"](?P<state>.*)[\'\"]\)$',
                action,
                re.IGNORECASE,
            )
            if match:
                result = match.group('state') in self.ctx.active
            else:
                # TODO: put error on 'error.execution' on internal event queue
                result = False
            return result
        raise Exception('incorrect condition provided to In() expression.')


@dataclass(frozen=True)
class DataModelProvider(ABC):
    """Instantiate state types from class metadata."""

    enabled: ClassVar[str] = 'default'
    # should support platform-specific, global, and local variables

    # def __init__(self, ctx: 'StateChart') -> None:
    #     """Initialize for MyPy."""
    #     self.__ctx = ctx

    # @property
    # def ctx(self) -> 'StateChart':
    #     """Return instance of StateChart."""
    #     return self.__ctx

    @property
    def evaluator(self) -> Type['EvaluatorBase']:
        """Get the configured evaluator expression language."""
        return In

    # @property
    # @abstractmethod
    # def location(self) -> Optional[Type['LocationBase']]:
    #     """Get the configured location expression language."""

    @property
    @abstractmethod
    def executor(self) -> Optional[Type['ExecutorBase']]:
        """Get the configured scripting expression language."""

    # TODO: need to handle foreach

    @classmethod
    def get_provider(cls, name: str) -> Type['DataModelProvider']:
        """Retrieve a data model implementation."""
        for provider in lookup_subclasses(cls):
            if name.lower() == provider.__name__.lower():
                return provider
        raise InvalidConfig('could not find provider context matching name')

    @classmethod
    def create(
        cls, settings: Union['DataModelProvider', str]
    ) -> 'DataModelProvider':
        """Factory for data model provider."""
        if isinstance(settings, DataModelProvider):
            return settings
        if isinstance(settings, str):
            Provider = cls.get_provider(cls.enabled.lower())
            if Provider:
                return Provider()
        raise InvalidConfig('could not find a valid data model configuration')
