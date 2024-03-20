"""Provide common types for statechart components."""

import json
from dataclasses import InitVar, dataclass
from mimetypes import guess_type
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    # Dict,
    List,
    Optional,
    # Sequence,
    Type,
    Union,
)
from urllib.request import urlopen

from superstate.provider import Default
from superstate.exception import InvalidConfig

# from superstate.utils import lookup_subclasses

if TYPE_CHECKING:
    from superstate.provider import Provider


@dataclass
class Data:
    """Data item providing state data."""

    id: str
    src: Optional[str] = None  # URI type
    expr: Optional[str] = None  # expression
    # TODO: need a more comprehensive binding strategy that removes iteration
    # for variable access
    binding: ClassVar[str] = 'early'
    content: InitVar[Optional[Any]] = None

    def __post_init__(self, content: Any = None) -> None:
        """Validate the data object."""
        self.__value: Optional[Any] = content
        if sum(1 for x in (self.expr, self.src, self.value) if x) > 1:
            raise InvalidConfig(
                'data contains mutually exclusive src and expr attributes'
            )
        if Data.binding == 'early':
            self.__initialize()

    def __initialize(self) -> None:
        """Process data attributes."""
        # TODO: if binding is late:
        #   - src: should store the URL and then retrieve when accessed
        #   - expr: should store and evalute using the assign datamodel element
        if self.expr:
            # TODO: use action or script specified in datamodel
            self.__value = self.expr
        if self.src:
            content_type, _ = guess_type(self.src)
            with urlopen(self.src) as rsp:
                content = rsp.read()
                if content_type == 'application/json':
                    self.__value = json.loads(content)
                else:
                    raise InvalidConfig('data is unsupported type')

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
                content=settings,
            )
        raise InvalidConfig('could not find a valid data configuration')

    @property
    def value(self) -> Optional[Any]:
        """Retrieve value from either expression or URL source."""
        if Data.binding == 'late':
            self.__initialize()
        return self.__value

    @value.setter
    def value(self, value: Any) -> None:
        """Set the value of the data attribute."""
        self.__value = value


@dataclass
class DataModel:
    """Instantiate state types from class metadata."""

    data: List['Data']
    # binding: ClassVar[str] = 'early'
    provider: ClassVar[Type['Provider']] = Default

    @classmethod
    def create(cls, settings: Union['DataModel', dict]) -> 'DataModel':
        """Return data model for data mapper."""
        if isinstance(settings, DataModel):
            return settings
        if isinstance(settings, dict):
            return cls(
                list(map(Data.create, settings['data']))
                if 'data' in settings
                else []
            )
        raise InvalidConfig('could not find a valid data model configuration')


@dataclass
class DoneData:
    """Data model providing state data."""

    param: List[Data]
    content: Optional[Any] = None
