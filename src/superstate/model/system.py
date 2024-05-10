"""Provide system info for statechart components."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, cast

from superstate.types import Identifier, Selection

if TYPE_CHECKING:
    from superstate.provider.data import DataModel


@dataclass
class Event:
    """Represent a system event."""

    name: str = cast(str, Identifier())
    kind: 'Selection' = field(
        default=Selection('platorm', 'internal', 'external')
    )
    sendid: str = field(default=cast(str, Identifier()))
    origin: Optional[str] = None  # URI
    origintype: Optional[str] = None
    invokeid: Optional[str] = None
    data: Optional['DataModel'] = None


@dataclass
class SystemSettings:
    """Provide system settings."""

    _name: str
    _event: 'Event'
    _sessionid: str
    # _ioprocessors: Sequence['Processor']
    _x: Optional['DataModel'] = None
