"""Provide common types for statechart components."""

from dataclasses import dataclass

# from typing import Any, ClassVar, Optional, Sequence, Type, Union
# from urllib.request import urlopen
#
# from superstate.exception import InvalidConfig
# from superstate.utils import lookup_subclasses


@dataclass
class Cancel:
    """Data item providing state data."""


@dataclass
class Finalize:
    """Data item providing state data."""


@dataclass
class Invoke:
    """Data item providing state data."""


@dataclass
class Param:
    """Data model providing para data for external services."""


#     name: str
#     expr: Optional[Any] = None  # value expression
#     location: Optional[str] = None  # locaiton expression


@dataclass
class Send:
    """Data item providing state data."""
