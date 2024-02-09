"""Provide common types for statechart components."""

from abc import ABC, abstractmethod  # pylint: disable=no-name-in-module
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Optional,
    Type,
    Union,
)

from superstate.exception import InvalidConfig
from superstate.model.expression.common import In
from superstate.utils import lookup_subclasses

if TYPE_CHECKING:
    from superstate.model.expression.base import ActionBase, ConditionBase


@dataclass
class DataModelProvider(ABC):
    """Instantiate state types from class metadata."""

    enabled: ClassVar[str] = 'default'
    # should support platform-specific, global, and local variables

    @property
    def conditional(self) -> Type['ConditionBase']:
        """Get the configured conditional expression language."""
        return In

    # @property
    # @abstractmethod
    # def location(self) -> Optional[Type['LocationBase']]:
    #     """Get the configured location expression language."""

    @property
    @abstractmethod
    def executor(self) -> Optional[Type['ActionBase']]:
        """Get the configured scripting expression language."""

    # TODO: need to handle foreach

    @classmethod
    def get_provider(cls, name: str) -> Type['DataModelProvider']:
        """Retrieve a data model implementation."""
        for provider in lookup_subclasses(cls):
            print('----------', provider)
            if name.lower() == provider.__name__.lower():
                return provider
        raise InvalidConfig('could not find provider context matching name')

    @classmethod
    def create(
        cls, settings: Union['DataModelProvider', str]
    ) -> 'DataModelProvider':
        """Return data model for data mapper."""
        if isinstance(settings, DataModelProvider):
            return settings
        if isinstance(settings, str):
            print(cls.enabled)
            Provider = cls.get_provider(cls.enabled.lower())
            if Provider:
                return Provider()
        raise InvalidConfig('could not find a valid data model configuration')
