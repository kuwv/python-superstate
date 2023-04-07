"""Provide superstate core statechart capability."""

import logging
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from superstate.exception import (
    InvalidConfig,
    InvalidState,
    InvalidTransition,
    ForkedTransition,
    GuardNotSatisfied,
)
from superstate.state import (
    AtomicState,
    CompositeState,
    CompoundState,
    ParallelState,
)

if TYPE_CHECKING:
    from superstate.state import State
    from superstate.transition import Transition

log = logging.getLogger(__name__)


class MetaStateChart(type):
    """Instantiate statecharts from class metadata."""

    _root: 'CompositeState'

    def __new__(
        cls,
        name: str,
        bases: Tuple[type, ...],
        attrs: Dict[str, Any],
    ) -> 'MetaStateChart':
        machine = (
            attrs.pop('__superstate__') if '__superstate__' in attrs else None
        )
        obj = super().__new__(cls, name, bases, attrs)
        if machine:
            obj._root = machine
        return obj


class StateChart(metaclass=MetaStateChart):
    """Represent statechart capabilities."""

    # __slots__ = ['__root', '__state', '__superstate', '__dict__', 'initial']
    __root: 'CompositeState'
    __superstate: 'CompositeState'

    def __init__(
        self,
        # *args: Any,
        **kwargs: Any,
    ) -> None:
        if 'logging_enabled' in kwargs and kwargs['logging_enabled']:
            handler = logging.StreamHandler()
            formatter = kwargs.pop(
                'logging_format', '%(name)s :: %(levelname)-8s :: %(message)s'
            )
            handler.setFormatter(logging.Formatter(fmt=formatter))
            log.addHandler(handler)
            if 'logging_level' in kwargs:
                log.setLevel(kwargs['logging_level'].upper())
        log.info('initializing statechart')

        if hasattr(self.__class__, '_root'):
            self.__root = deepcopy(self.__class__._root)
        elif 'superstate' in kwargs:
            self.__root = deepcopy(kwargs['superstate'])
        else:
            raise InvalidConfig(
                'attempted initialization with empty superstate'
            )
        self.__superstate = self.__root
        # TODO: need to traverse initial or handle callable
        self.__superstate.initial = kwargs.get(
            'initial',
            self.__root.initial if hasattr(self.__root, 'initial') else None,
        )
        log.info('loaded states and transitions')

        if kwargs.get('enable_start_transition', True):
            self.superstate.run_on_entry(self)
            self.state.run_on_entry(self)
        log.info('statechart initialization complete')

    def __getattr__(self, name: str) -> Any:
        # do not attempt to resolve missing dunders
        if name.startswith('__'):
            raise AttributeError

        # handle state check locally
        if name.startswith('is_'):
            return self.superstate.is_active(name[3:])

        # handle automatic transitions
        if name == '_auto_':
            def wrapper(*args: Any, **kwargs: Any) -> None:
                return self.trigger('', *args, **kwargs)
            return wrapper

        # directly transition by event name
        # if name.startswith('to_'):
        for transition in self.transitions:
            if transition.event in ('_auto_', name):
                # def wrapper(*args: Any, **kwargs: Any) -> None:
                #     return (getattr(self, 'get_transition')).run(
                #         name, *args, **kwargs
                #     )
                #
                # return wrapper

                # if transition.evaluate(self, *args, **kwargs):
                #     result = transition.callback().__get__(
                #         self, self.__class__
                #     )
                # else:
                result = self.trigger(name)
                return result

        # retrieve substate by name
        for key in list(self.states):
            if key == name:
                return self.superstate.substates[name]
        raise AttributeError

    @property
    def superstate(self) -> 'CompositeState':
        """Return superstate."""
        return self.__superstate

    @property
    def state(self) -> 'State':
        """Return the current state."""
        try:
            return self.superstate.substate
        except Exception as err:
            log.error(err)
            raise KeyError('state is undefined') from err

    @property
    def states(self) -> Tuple['State', ...]:
        """Return list of states."""
        return tuple(self.superstate.substates.values())

    def change_state(
        self,
        statepath: str,
        skip_triggers: bool = False,
        skip_on_entry: bool = False,
        skip_on_exit: bool = False,
    ) -> None:
        """Change current state to target state."""
        log.info('changing state from %s', statepath)
        if not skip_triggers or not skip_on_exit:
            self.state.run_on_exit(self)
        state = self.get_state(statepath)
        if self.superstate != state.superstate:
            self.__superstate = state.superstate
        self.__superstate.substate = state.name
        if not skip_triggers or not skip_on_entry:
            self.state.run_on_entry(self)
        log.info('changed state to %s', statepath)

    def get_state(self, statepath: str) -> 'State':
        """Get state from query path."""
        log.info('lookup state at path %r', statepath)
        subpaths = statepath.split('.')

        current: 'State' = self.__root
        if statepath.startswith('..'):
            current = self.superstate
            for p in subpaths:
                if p == '':
                    current = current.superstate  # type: ignore
                else:
                    break
        elif statepath.startswith('.'):
            current = self.state

        for i, state in enumerate(subpaths):
            if current != state and isinstance(current, CompoundState):
                current = current.substates[state]
            if i == (len(subpaths) - 1):
                log.info('found state %s', current)
                return current
        raise InvalidState(f"state could not be found: {statepath}")

    def add_state(
        self, state: 'State', statepath: Optional[str] = None
    ) -> None:
        """Add state to either superstate or target state."""
        superstate = (
            self.get_state(statepath) if statepath else self.superstate
        )
        if isinstance(superstate, CompositeState):
            superstate.add_state(state)
            log.info('added state %s', state.name)
        else:
            raise InvalidState(
                f"cannot add state to non-composite state {superstate.name}"
            )

    @property
    def transitions(self) -> Tuple['Transition', ...]:
        """Return list of current transitions."""
        # return tuple(
        #     self.state.transitions + self.superstate.transitions
        #     if self.state != self.superstate
        #     and hasattr(self.state, 'transitions')
        #     else self.superstate.transitions
        # )
        return (
            tuple(self.state.transitions)
            if hasattr(self.state, 'transitions')
            else ()
        )

    def add_transition(
        self, transition: 'Transition', statepath: Optional[str] = None
    ) -> None:
        """Add transition to either superstate or target state."""
        target = self.get_state(statepath) if statepath else self.superstate
        if isinstance(target, AtomicState):
            target.add_transition(transition)
            log.info('added transition %s', transition.event)
        else:
            raise InvalidState('cannot add transition to %s', target)

    @staticmethod
    def _lookup_transitions(event: str, state: 'State') -> List["Transition"]:
        return (
            state.get_transition(event)
            if hasattr(state, 'get_transition')
            else None
        )

    def process_transitions(
        self, event: str, *args: Any, **kwargs: Any
    ) -> 'Transition':
        """Get transition event from active states."""
        # child => parent => grandparent
        guarded: List['Transition'] = []
        current: Optional['State'] = self.state
        while current:
            transitions: List['Transition'] = []

            # search parallelstates for transitions
            if isinstance(current, ParallelState):
                for state in current.substates:
                    transitions += self._lookup_transitions(event, state)
            else:
                transitions = self._lookup_transitions(event, current)

            # evaluate guards
            allowed = [
                t for t in transitions if t.evaluate(self, *args, **kwargs)
            ]
            if allowed:
                if len(allowed) > 1:
                    raise ForkedTransition(
                        'More than one transition was allowed for this event'
                    )
                return allowed[0]
            current = self.superstate if current != self.superstate else None
            guarded += transitions
        if len(guarded) != 0:
            raise GuardNotSatisfied('no transition possible from state')
        raise InvalidTransition(f"transition could not be found: {event}")

    def trigger(
        self, event: str, /, *args: Any, **kwargs: Any
    ) -> Optional[Any]:
        """Transition from event to target state."""
        transition = self.process_transitions(event)
        if transition:
            log.info('transitioning to %r', event)
            result = transition.run(self, *args, **kwargs)
            return result
        raise InvalidTransition('transition %r not found', event)
