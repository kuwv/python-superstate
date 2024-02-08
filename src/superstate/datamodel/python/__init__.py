"""Provide common types for statechart components."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Type

from superstate.datamodel.base import DataModel
from superstate.datamodel.python.executor import Action
from superstate.datamodel.python.evaluator import Condition

if TYPE_CHECKING:
    from superstate.model.expression.base import ActionBase, ConditionBase


@dataclass
class Default(DataModel):
    """Default data model providing state data."""

    @property
    def conditional(self) -> Type['ConditionBase']:
        """Get the configured conditional expression language."""
        return Condition

    @property
    def executor(self) -> Optional[Type['ActionBase']]:
        """Get the configured scripting expression language."""
        return Action
