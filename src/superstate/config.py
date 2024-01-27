"""Provide statechart settings for superstate."""

from typing import TYPE_CHECKING, Iterable, Type

from superstate.model import Null, Python

if TYPE_CHECKING:
    from superstate.model import DataModel

DEFAULT_BINDING: str = 'early'

DEFAULT_DATAMODEL: str = 'null'
ENABLED_DATAMODELS: Iterable[Type['DataModel']] = (
    Null,
    # ECMAScript,
    Python  # platform-specific
    # XPath,
)
