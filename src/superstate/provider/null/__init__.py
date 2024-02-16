"""Provide common types for statechart components."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Type

from superstate.provider.base import DataModelProvider

if TYPE_CHECKING:
    from superstate.provider.base import ExecutorBase


@dataclass(frozen=True)
class Null(DataModelProvider):
    """Data model providing state data without any scripting capabilities."""

    @property
    def executor(self) -> Optional[Type['ExecutorBase']]:
        """Get the configured executor expression language."""
        return None

    @property
    def dispatcher(self) -> Optional[Type['ExecutorBase']]:
        """Get the configured dispatcher expression language."""
        return None
