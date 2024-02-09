"""Provide common types for statechart components."""

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Optional,
    Type,
)

from superstate.provider.base import DataModelProvider

if TYPE_CHECKING:
    from superstate.model.expression.base import ActionBase


@dataclass
class Null(DataModelProvider):
    """Data model providing state data without any scripting capabilities."""

    @property
    def executor(self) -> Optional[Type['ActionBase']]:
        """Get the configured scripting expression language."""
        return None
