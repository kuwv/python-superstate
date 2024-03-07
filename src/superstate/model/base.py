"""Provide common types for statechart components."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Union

from superstate.exception import InvalidConfig
from superstate.types import Expression
from superstate.utils import lookup_subclasses

if TYPE_CHECKING:
    from superstate.provider import Provider


class ExecutableContent:
    """Baseclass for expressions."""

    @classmethod
    def create(
        cls, settings: Union['ExecutableContent', Callable, Dict[str, Any]]
    ) -> 'ExecutableContent':
        """Create expression from configuration."""
        if isinstance(settings, ExecutableContent):
            return settings
        if isinstance(settings, dict):
            for key, value in settings.items():
                for Subclass in lookup_subclasses(cls):
                    if Subclass.__name__.lower() == key.lower():
                        return (
                            Subclass(value)  # type: ignore
                            if callable(value)
                            else Subclass(**value)
                        )
        raise InvalidConfig('could not find a valid configuration for action')

    def callback(
        self, provider: 'Provider', *args: Any, **kwargs: Any
    ) -> Optional[Any]:
        """Provide callback for language provider."""


class Action(ExecutableContent):
    """Base class for actions."""

    # XXX: action is a specialized remote

    @classmethod
    def create(
        cls, settings: Union['ExecutableContent', Callable, Dict[str, Any]]
    ) -> 'ExecutableContent':
        """Create action from configuration."""
        if isinstance(settings, str) or callable(settings):
            for Subclass in lookup_subclasses(cls):
                if Subclass.__name__.lower() == 'script':
                    return Subclass(settings)  # type: ignore
        return super().create(settings)


@dataclass
class Conditional(ExecutableContent):
    """Data item providing state data."""

    cond: Union[Expression, bool]

    @classmethod
    def create(
        cls, settings: Union['ExecutableContent', Callable, Dict[str, Any]]
    ) -> 'ExecutableContent':
        """Create state from configuration."""
        if isinstance(settings, (bool, str)) or callable(settings):
            return cls(settings)  # type: ignore
        return super().create(settings)

    def callback(
        self, provider: 'Provider', *args: Any, **kwargs: Any
    ) -> Optional[Any]:
        """Provide callback for language provider."""
        return provider.eval(self.cond, *args, **kwargs)
