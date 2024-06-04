"""Provide common types for statechart components."""

import json
from collections import ChainMap
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
from superstate.exception import InvalidConfig, SuperstateException

# from superstate.utils import lookup_subclasses

if TYPE_CHECKING:
    from superstate.state import State
    from superstate.provider import Provider


@dataclass
class Data:
    """Data item providing state data."""

    id: str
    src: Optional[str] = None  # URI type
    expr: Optional[str] = None  # expression
    settings: InitVar[Optional[Any]] = None

    def __post_init__(self, settings: Any) -> None:
        """Validate the data object."""
        self.__value: Optional[Any] = settings if settings else None
        if sum(1 for x in (self.__value, self.expr, self.src) if x) > 1:
            raise InvalidConfig(
                'data contains mutually exclusive src and expr attributes'
            )

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
                settings=settings,
            )
        raise InvalidConfig('could not find a valid data configuration')

    @property
    def value(self) -> Optional[Any]:
        """Retrieve value from either expression or URL source."""
        # TODO: if binding is late:
        #   - src: should store the URL and then retrieve when accessed
        #   - expr: should store and evalute using the assign datamodel element
        if self.expr is not None:
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
        return self.__value


@dataclass
class DataModel(ChainMap):
    """Instantiate state types from class metadata."""

    data: List['Data']
    binding: ClassVar[str] = 'early'
    provider: ClassVar[Type['Provider']] = Default

    def __post_init__(self) -> None:
        """Validate the data object."""
        self.__parent: Optional['State'] = None
        # self.__provider: Optional['Provider'] = None

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

    @property
    def parent(self) -> Optional['State']:
        """Get parent state."""
        return self.__parent

    @parent.setter
    def parent(self, state: 'State') -> None:
        if self.__parent is None:
            self.__parent = state
            # self.maps.insert(0, self.parent.datamodel)
            # self.__provider = DataModel.provider(self.__parent)
        else:
            raise SuperstateException('cannot change parent for state')

    def populate(self) -> None:
        """Populate the data items for the datamodel."""
        # data = {}
        # for x in self.data:
        #     if x.expr:
        #         data[x.id] = self.__provider.exec(x.expr)
        #     if x.src:
        #         content_type, _ = guess_type(x.src)
        #         with urlopen(x.src) as rsp:
        #             content = rsp.read()
        #             if content_type == 'application/json':
        #                 data[x.id] = json.loads(content)
        #             else:
        #                 raise InvalidConfig('data is unsupported type')
        # super().__init__(data)
        super().__init__({x.id: x.value for x in self.data})


@dataclass
class DoneData:
    """Data model providing state data."""

    param: List[Data]
    content: Optional[Any] = None
