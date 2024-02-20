"""Provide common types for statechart components."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Union

from superstate.exception import InvalidConfig
from superstate.utils import lookup_subclasses

if TYPE_CHECKING:
    from superstate.provider import Provider


class Action(ABC):
    """Base class for actions."""

    @classmethod
    def create(cls, settings: Union['Action', Dict[str, Any]]) -> 'Action':
        """Create state from configuration."""
        if isinstance(settings, Action):
            return settings
        if isinstance(settings, dict):
            for key, values in settings.items():
                for subclass in lookup_subclasses(cls):
                    if subclass.__name__.lower() == key.lower():
                        return subclass(**values)
        raise InvalidConfig('could not find a valid action configuration')

    @abstractmethod
    def callback(self, provider: 'Provider') -> None:
        """Provide callback for language provider."""
