"""Provide system info for statechart components."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, NotRequired, Optional, TypedDict, cast

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


# Specify the boolean expression language used as the value of the 'cond'
# attribute in <transition>, <if> and <elseif> This language MUST not have side
# effects and MUST include the predicate 'In', which takes a single argument,
# the id of a state in the enclosing state machine, and returns 'true' if the
# state machine is in that state.
#
# Specify the location expression language that is used as the value of the
# 'location' attribute of the <assign> tag.
#
# Specify the value expression language that is used as the value of the 'expr'
# attribute of the <data> and <assign> elements.
#
# Specify the scripting language used inside the <script> element


class HostInfo(TypedDict):
    """Provide settings for host info."""

    hostname: str
    url: NotRequired[str]


class PlatformInfo(TypedDict):
    """Provide settings for platform settings."""

    arch: str
    release: str
    system: str
    processor: str


class RuntimeInfo(TypedDict):
    """Provide settings for python info."""

    implementation: str
    version: str


class TimeInfo(TypedDict):
    """Provide settings for timezone info."""

    initialized: str
    timezone: str
    # offset: str


class SystemInfo(TypedDict):
    """Provide system info."""

    host: NotRequired['HostInfo']
    time: NotRequired['TimeInfo']
    runtime: NotRequired['RuntimeInfo']
    platform: NotRequired['PlatformInfo']
