"""Provide common types for statechart components."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Type

from superstate.provider.base import Provider
from superstate.provider.default.executor import Executor
from superstate.provider.default.evaluator import Evaluator

if TYPE_CHECKING:
    from superstate.provider.base import EvaluatorBase, ExecutorBase


@dataclass(frozen=True)
class Default(Provider):
    """Default data model providing state data."""

    # TODO: pull config from system settings within DataModel to configure
    # layout

    # @property
    # def dispatcher(self) -> Type['DispatcherBase']:
    #     """Get the configured dispath expression language."""

    @property
    def evaluator(self) -> Type['EvaluatorBase']:
        """Get the configured evaluator expression language."""
        return Evaluator

    @property
    def executor(self) -> Optional[Type['ExecutorBase']]:
        """Get the configured scripting expression language."""
        return Executor
