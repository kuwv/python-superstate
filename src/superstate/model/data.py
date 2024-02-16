"""Provide common types for statechart components."""

from dataclasses import InitVar, dataclass, field
from typing import Any, ClassVar, Optional, Sequence, Union
from urllib.request import urlopen

from superstate.exception import InvalidConfig


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
class DataModel:
    """Instantiate state types from class metadata."""

    enabled: ClassVar[str] = 'default'
    data: Sequence['Data'] = field(default_factory=list)
    # should support platform-specific, global, and local variables

    @classmethod
    def create(cls, settings: Union['DataModel', dict]) -> 'DataModel':
        """Return data model for data mapper."""
        if isinstance(settings, DataModel):
            return settings
        if isinstance(settings, dict):
            return cls(
                tuple(map(Data.create, settings['data']))
                if 'data' in settings
                else []
            )
        raise InvalidConfig('could not find a valid data model configuration')


@dataclass
class DoneData:
    """Data model providing state data."""

    param: Sequence[Data]
    content: Optional[Any] = None
