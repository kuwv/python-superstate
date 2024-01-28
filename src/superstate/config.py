"""Provide statechart settings for superstate."""

from typing import TYPE_CHECKING, Iterable, Type

from superstate.model import Null, Default

if TYPE_CHECKING:
    from superstate.model import DataModel

DEFAULT_BINDING: str = 'early'

DEFAULT_DATAMODEL: str = 'default'
ENABLED_DATAMODELS: Iterable[Type['DataModel']] = (
    Default,  # platform-specific
    Null,
    # ECMAScript,
    # XPath,
)
