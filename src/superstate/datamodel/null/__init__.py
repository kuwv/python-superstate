"""Provide common types for statechart components."""

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Optional,
    Type,
)

from superstate.datamodel.base import DataModel

if TYPE_CHECKING:
    from superstate.model.expression.base import ActionBase


@dataclass
class Null(DataModel):
    """Data model providing state data without any scripting capabilities."""

    @property
    def executor(self) -> Optional[Type['ActionBase']]:
        """Get the configured scripting expression language."""
        return None
