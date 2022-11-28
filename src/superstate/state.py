"""Provide states for statechart."""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union, cast

from superstate.common import Action
from superstate.exception import InvalidConfig
from superstate.transition import Transition, transitions
from superstate.types import NameDescriptor

if TYPE_CHECKING:
    from superstate.machine import StateChart
    from superstate.types import (
        EventActions,
        InitialType,
    )

log = logging.getLogger(__name__)


# class MetaState(type):
#     """Instantiate state types from class metadata."""
#
#     # _initial: Optional[Union[Callable, str]]
#     _states: List['State']
#     _transitions: List['State']
#     # _on_entry:
#     # _on_exit:
#
#     def __new__(
#         cls,
#         name: str,
#         bases: Tuple[type, ...],
#         attrs: Dict[str, Any],
#     ) -> 'MetaState':
#         # initial = attrs.pop('initial', None)
#         # kind = attrs.pop('kind')
#         states = attrs.pop('__states__', None)
#         transitions = attrs.pop('__transitions__', None)
#         # on_entry = attrs.pop('on_entry', None)
#         # on_exit = attrs.pop('on_exit', None)
#
#         obj = type.__new__(cls, name, bases, attrs)
#         # obj._initial = states
#         obj._states = states
#         obj._transitions = transitions
#         # obj._on_entry = on_entry
#         # obj._on_exit = on_exit
#
#         return obj


class State:
    """Manage state representation for statechart."""

    __slots__ = [
        '_name',
        '__initial',
        '__substate',
        '__substates',
        '__transitions',
        '__on_entry',
        '__on_exit',
        '__kind',
        '__dict__',
    ]
    name = cast(str, NameDescriptor('_name'))
    __initial: Optional['InitialType']
    __on_entry: Optional['EventActions']
    __on_exit: Optional['EventActions']

    def __init__(
        self,
        name: str,
        # *args: Any,
        **kwargs: Any,
    ) -> None:
        if not name.replace('_', '').isalnum():
            raise InvalidConfig('state name contains invalid characters')
        self.name = name
        self.__kind = kwargs.get('kind')
        self.__substate = self

        self.__substates = {x.name: x for x in kwargs.get('states', [])}
        self.__transitions = kwargs.get('transitions', [])
        for transition in self.transitions:
            self.__register_transition_callback(transition)

        self.__initial = kwargs.get('initial')
        self.__history = (
            kwargs.get('history', 'shallow')
            if self.kind == 'history'
            else None
        )
        # FIXME: pseudostates should not include triggers
        self.__on_entry = kwargs.get('on_entry')
        self.__on_exit = kwargs.get('on_exit')

        self.__validate_state()

    def __repr__(self) -> str:
        return repr(f"State({self.name})")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, State):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return False

    def __register_transition_callback(self, transition: 'Transition') -> None:
        # XXX: currently mapping to class instead of instance
        # TODO: need way to provide auto-transition
        setattr(
            self,
            transition.event if transition.event != '' else '_auto_',
            transition.callback().__get__(self, self.__class__),
        )

    def __validate_state(self) -> None:
        # TODO: empty statemachine should default to null event
        if self.kind == 'compund':
            if len(self.__substates) < 2:
                raise InvalidConfig('There must be at least two states')
            if not self.initial:
                raise InvalidConfig('There must exist an initial state')
        if self.initial and self.kind == 'parallel':
            raise InvalidConfig(
                'parallel state should not have an initial state'
            )
        if self.kind == 'final' and self.__on_exit:
            log.warning('final state will never run "on_exit" action')
        log.info('evaluated state')

    @property
    def initial(self) -> Optional['InitialType']:
        """Return initial substate if defined."""
        return self.__initial

    @property
    def kind(self) -> str:
        """Return state type."""
        if self.__kind:
            kind = self.__kind
        elif self.substates != {} and self.transitions:
            for transition in self.transitions:
                if transition == '':
                    kind = 'transient'
                    break
            else:
                kind = 'compound'
        elif self.substates != {}:
            if not self.initial:
                kind = 'parallel'
            kind = 'compound'
        else:
            # XXX: can auto to final - if self.transitions != []: else 'final'
            kind = 'atomic'
        return kind

    @property
    def history(self) -> Optional[str]:
        """Return previous substate."""
        return self.__history

    @property
    def substate(self) -> 'State':
        """Current substate of this state."""
        return self.__substate

    @property
    def substates(self) -> Dict[str, 'State']:
        """Return substates."""
        return self.__substates

    @property
    def transitions(self) -> Tuple['Transition', ...]:
        """Return transitions of this state."""
        return tuple(self.__transitions)

    def add_state(self, state: 'State') -> None:
        """Add substate to this state."""
        self.__substates[state.name] = state

    def add_transition(self, transition: 'Transition') -> None:
        """Add transition to this state."""
        self.__transitions.append(transition)
        self.__register_transition_callback(transition)

    def get_transition(self, event: str) -> Tuple['Transition', ...]:
        """Get each transition maching event."""
        return tuple(
            filter(
                lambda transition: transition.event == event, self.transitions
            )
        )

    def _run_on_entry(self, machine: 'StateChart') -> None:
        if self.__on_entry is not None and self.kind != 'history':
            Action(machine).run(self.__on_entry)
            log.info(
                "executed 'on_entry' state change action for %s", self.name
            )

    def _run_on_exit(self, machine: 'StateChart') -> None:
        if self.__on_exit is not None and self.kind != 'history':
            Action(machine).run(self.__on_exit)
            log.info(
                "executed 'on_exit' state change action for %s", self.name
            )


def state(config: Union['State', dict, str]) -> 'State':
    """Create state from configuration."""
    if isinstance(config, State):
        return config
    if isinstance(config, str):
        return State(config)
    if isinstance(config, dict):
        cls = config.get('factory', State)
        return cls(
            name=config.get('name', 'superstate'),
            initial=config.get('initial'),
            kind=config.get('kind'),
            states=(states(*config['states']) if 'states' in config else []),
            transitions=(
                transitions(*config['transitions'])
                if 'transitions' in config
                else []
            ),
            on_entry=config.get('on_entry'),
            on_exit=config.get('on_exit'),
        )
    raise InvalidConfig('could not find a valid state configuration')


def states(*args: Any) -> List['State']:
    """Create states from configuration."""
    return list(map(state, args))
