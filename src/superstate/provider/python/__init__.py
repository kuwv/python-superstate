"""Provide common types for statechart components."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Type

from superstate.provider.base import DataModelProvider
from superstate.provider.python.executor import Action
from superstate.provider.python.evaluator import Condition

if TYPE_CHECKING:
    from superstate.model.expression.base import ActionBase, ConditionBase


@dataclass
class Default(DataModelProvider):
    """Default data model providing state data."""

    # TODO: pull config from system settings within DataModel to configure
    # layout

    @property
    def conditional(self) -> Type['ConditionBase']:
        """Get the configured conditional expression language."""
        return Condition

    @property
    def executor(self) -> Optional[Type['ActionBase']]:
        """Get the configured scripting expression language."""
        return Action
