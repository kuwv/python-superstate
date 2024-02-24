"""Provide common types for statechart components."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Dict, Union

from superstate.exception import InvalidConfig
from superstate.utils import lookup_subclasses

if TYPE_CHECKING:
    from superstate.provider import Provider


class Expression:
    """Baseclass for expressions."""

    @classmethod
    def create(
        cls, settings: Union['Action', Callable, Dict[str, Any]]
    ) -> 'Action':
        """Create expression from configuration."""
        if isinstance(settings, Expression):
            print('-- action', settings)
            return settings
        if isinstance(settings, dict):
            print('-- dict', settings)
            for key, value in settings.items():
                for Subclass in lookup_subclasses(cls):
                    if Subclass.__name__.lower() == key.lower():
                        print('-- value', key, value, Subclass)
                        return (
                            Subclass(value)  # type: ignore
                            if callable(value)
                            else Subclass(**value)
                        )
        raise InvalidConfig('could not find a valid configuration for action')

    def callback(self, provider: 'Provider') -> None:
        """Provide callback for language provider."""


class Action(Expression):
    """Base class for actions."""

    @classmethod
    def create(
        cls, settings: Union['Action', Callable, Dict[str, Any]]
    ) -> 'Action':
        """Create action from configuration."""
        print(settings)
        if isinstance(settings, str) or callable(settings):
            print('-- callable', settings)
            for Subclass in lookup_subclasses(cls):
                if Subclass.__name__.lower() == 'script':
                    print('-- made it', Subclass, settings)
                    return Subclass(settings)  # type: ignore
        print('fail', settings)
        return super().create(settings)


@dataclass
class Conditional(Expression):
    """Data item providing state data."""

    cond: Union[Callable, bool, str]

    @classmethod
    def create(
        cls, settings: Union['Action', Callable, Dict[str, Any]]
    ) -> 'Action':
        """Create state from configuration."""
        print(settings)
        if isinstance(settings, (bool, str)) or callable(settings):
            print('-- callable', settings)
            return cls(settings)  # type: ignore
        print('fail', settings)
        return super().create(settings)
