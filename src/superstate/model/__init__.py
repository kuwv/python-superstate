"""Provide common types for statechart components."""

from abc import ABC, abstractmethod  # pylint: disable=no-name-in-module
from dataclasses import InitVar, dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Sequence,
    Optional,
    Type,
    Union,
)
from urllib.request import urlopen

from superstate.exception import InvalidConfig
from superstate.model.common import In
from superstate.model.default import Action, Guard
from superstate.types import Selection
from superstate.utils import lookup_subclasses

if TYPE_CHECKING:
    from superstate.types import ActionBase, GuardBase


@dataclass
class Assign:
    """Data item providing state data."""

    location: str
    expr: Optional[Any] = None  # expression


@dataclass
class Data:
    """Data item providing state data."""

    id: str
    src: InitVar[Optional[str]] = None  # URI type
    expr: InitVar[Optional[str]] = None  # expression
    value: Optional[Any] = field(repr=False, default=None)

    def __post_init__(self, src: Optional[str], expr: Optional[str]) -> None:
        """Validate the data object."""
        if sum(1 for x in (src, expr, self.value) if x) > 1:
            raise Exception(
                'data contains mutually exclusive src, expr, or value attrs'
            )
        if src:
            with urlopen(src) as rsp:
                self.value = rsp.read()
        if expr:
            # TODO: use action or script specified in datamodel
            self.value = expr

        # TODO: if binding is late:
        #   - src should store the URL and then retrieve when accessed
        #   - expr should store and evalute using the datamodel scripting
        #     language

    @classmethod
    def create(cls, settings: Union['Data', dict]) -> 'Data':
        """Return data object for data mapper."""
        if isinstance(settings, Data):
            return settings
        if isinstance(settings, dict):
            return cls(
                id=settings.pop('id'),
                src=settings.pop('src', None),
                expr=settings.pop('expr', None),
                value=settings,
            )
        raise InvalidConfig('could not find a valid data configuration')


@dataclass
class DoneData:
    """Data model providing state data."""

    param: Sequence[Data]
    content: Optional[Any] = None


@dataclass
class Event:
    """Represent a system event."""

    name: str
    kind: 'Selection' = field(
        default=Selection('platorm', 'internal', 'external')
    )
    # sendid: str
    origin: Optional[str] = None  # URI
    origintype: Optional[str] = None
    invokeid: Optional[str] = None
    data: Optional['DataModel'] = None


@dataclass
class Param:
    """Data model providing para data for external services."""

    name: str
    expr: Optional[Any] = None  # value expression
    location: Optional[str] = None  # locaiton expression


# @dataclass
# class Script:
#     """Data model providing para data for external services."""
#
#     src: str


@dataclass
class DataModel(ABC):
    """Instantiate state types from class metadata."""

    enabled: ClassVar[str] = 'default'
    data: Sequence['Data'] = field(default_factory=list)

    @property
    def conditional(self) -> Type['GuardBase']:
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
    def create(cls, settings: Union['DataModel', dict]) -> 'DataModel':
        """Return data model for data mapper."""
        if isinstance(settings, DataModel):
            return settings
        if isinstance(settings, dict):
            for datamodel in lookup_subclasses(cls):
                if cls.enabled.lower() == datamodel.__name__.lower():
                    return datamodel(
                        tuple(map(Data.create, settings['data']))
                        if 'data' in settings
                        else []
                    )
        raise InvalidConfig('could not find a valid data model configuration')


@dataclass
class Null(DataModel):
    """Data model providing state data without any scripting capabilities."""

    @property
    def executor(self) -> Optional[Type['ActionBase']]:
        """Get the configured scripting expression language."""
        return None


# @dataclass
# class ECMAScript(DataModel):
#     "Data mode providing state data with scripting using ECMAScript."""


@dataclass
class Default(DataModel):
    """Default data model providing state data."""

    @property
    def conditional(self) -> Type['GuardBase']:
        """Get the configured conditional expression language."""
        return Guard

    @property
    def executor(self) -> Optional[Type['ActionBase']]:
        """Get the configured scripting expression language."""
        return Action


@dataclass
class SystemSettings:
    """Provide system settings."""

    _name: str
    _event: 'Event'
    _sessionid: str
    # _ioprocessors: Sequence['EventProcessor']
    _x: Optional['DataModel'] = None
