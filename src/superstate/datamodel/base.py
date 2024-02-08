"""Provide common types for statechart components."""

from abc import ABC, abstractmethod  # pylint: disable=no-name-in-module
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Sequence,
    Optional,
    Type,
    Union,
)

from superstate.exception import InvalidConfig
from superstate.model.data import Data
from superstate.model.expression.common import In
from superstate.utils import lookup_subclasses

if TYPE_CHECKING:
    from superstate.model.expression.base import ActionBase, ConditionBase


@dataclass
class DataModel(ABC):
    """Instantiate state types from class metadata."""

    enabled: ClassVar[str] = 'default'
    data: Sequence['Data'] = field(default_factory=list)
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
    def get_datamodel(cls, name: str) -> Type['DataModel']:
        """Retrieve a data model implementation."""
        for datamodel in lookup_subclasses(cls):
            if name.lower() == datamodel.__name__.lower():
                return datamodel
        raise InvalidConfig('could not find DataModel matching name')

    @classmethod
    def create(cls, settings: Union['DataModel', dict]) -> 'DataModel':
        """Return data model for data mapper."""
        if isinstance(settings, DataModel):
            return settings
        if isinstance(settings, dict):
            datamodel = cls.get_datamodel(cls.enabled.lower())
            if datamodel:
                return datamodel(
                    tuple(map(Data.create, settings['data']))
                    if 'data' in settings
                    else []
                )
        raise InvalidConfig('could not find a valid data model configuration')
