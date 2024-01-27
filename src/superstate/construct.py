"""Construct components for statechart."""

from typing import TYPE_CHECKING, Any, List, Union

from superstate.config import (
    # DEFAULT_BINDING,
    DEFAULT_DATAMODEL,
    ENABLED_DATAMODELS,
)
from superstate.exception import (
    InvalidConfig,
    # InvalidState,
    # InvalidTransition,
    # GuardNotSatisfied,
)
from superstate.model import Data, DataModel
from superstate.state import State
from superstate.transition import Transition

if TYPE_CHECKING:
    from superstate.state import CompositeState

__all__ = (
    'data',
    'datamodel',
    'state',
    'states',
    'transition',
    'transitions',
)


def data(settings: Union['Data', dict]) -> 'Data':
    """Return data object for data mapper."""
    if isinstance(settings, Data):
        return settings
    if isinstance(settings, dict):
        return Data(
            id=settings.pop('id'),
            src=settings.pop('src', None),
            expr=settings.pop('expr', None),
            value=settings,
        )
    raise InvalidConfig('could not find a valid data configuration')


def datamodel(settings: Union['DataModel', dict]) -> 'DataModel':
    """Return data model for data mapper."""
    if isinstance(settings, DataModel):
        return settings
    if isinstance(settings, dict):
        for dm in ENABLED_DATAMODELS:
            if (DEFAULT_DATAMODEL or 'null').lower() == dm.__name__.lower():
                return dm(
                    tuple(map(data, settings['data']))
                    if 'data' in settings
                    else []
                )
    raise InvalidConfig('could not find a valid data model configuration')


def transition(settings: Union['Transition', dict]) -> 'Transition':
    """Create transition from configuration."""
    if isinstance(settings, Transition):
        return settings
    if isinstance(settings, dict):
        return Transition(
            event=settings.get('event', ''),
            target=settings['target'],  # XXX: should allow optional
            action=settings.get('action'),
            cond=settings.get('cond'),
            # kind=settings.get('type', 'internal'),
        )
    raise InvalidConfig('could not find a valid transition configuration')


def transitions(*args: Any) -> List['Transition']:
    """Create transitions from configuration."""
    return list(map(transition, args))


def state(
    settings: Union['State', dict, str],
    # constructor: Type['State'] = State,
    # **kwargs: Any,
) -> Union['CompositeState', 'State']:
    """Create state from configuration."""
    obj = None
    if isinstance(settings, State):
        obj = settings
    elif isinstance(settings, dict):
        obj = settings.pop('factory', State)(
            name=settings.get('name', 'root'),
            initial=settings.get('initial'),
            type=settings.get('type'),
            datamodel=datamodel(settings.get('datamodel', {})),
            states=(
                states(*settings['states']) if 'states' in settings else []
            ),
            transitions=(
                transitions(*settings['transitions'])
                if 'transitions' in settings
                else []
            ),
            on_entry=settings.get('on_entry'),
            on_exit=settings.get('on_exit'),
        )
    elif isinstance(settings, str):
        obj = State(settings)
    if obj:
        return obj
    raise InvalidConfig('could not find a valid state configuration')


def states(*args: Any) -> List['State']:
    """Create states from configuration."""
    return list(map(state, args))
