"""Provide superstate core statechart capability."""

import logging
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

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
    # ParallelState,
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

    # __slots__ = ['__states', '__dict__']
    __root: 'CompositeState'
    __state: 'State'
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
            superstate = deepcopy(self.__class__._root)
        elif 'superstate' in kwargs:
            superstate = deepcopy(kwargs['superstate'])
        else:
            raise InvalidConfig(
                'attempted initialization with empty superstate'
            )
        self.__state = self.__root = superstate

        self.initial = kwargs.get('initial', self.__root.initial)
        if self.initial:
            self.__state = self.get_state(
                self.initial(self) if callable(self.initial) else self.initial
            )
        log.info('loaded states and transitions')

        if kwargs.get('enable_start_transition', True):
            self.state.run_on_entry(self)
        log.info('statechart initialization complete')

    def __getattr__(self, name: str) -> Any:
        if name.startswith('__'):
            raise AttributeError

        if name.startswith('is_'):
            return self.superstate.is_current_state(name)

        for transition in self.transitions:
            if transition.event == name or (
                transition.event == '' and name == '_auto_'
            ):
                return transition.callback().__get__(self, self.__class__)

        for key in list(self.states):
            if key == name:
                return self.superstate.substates[name]
        raise AttributeError

    @property
    def transitions(self) -> Tuple['Transition', ...]:
        """Return list of current transitions."""
        return (
            tuple(self.state.transitions)
            if hasattr(self.state, 'transitions')
            else ()
        )
        # return tuple(
        #     self.state.transitions + self.superstate.transitions
        #     if self.state != self.superstate
        #     and hasattr(self.state, 'transitions')
        #     else self.superstate.transitions
        # )

    @property
    def superstate(self) -> 'CompositeState':
        """Return superstate."""
        return self.__state.superstate or self.__root

    @property
    def state(self) -> 'State':
        """Return the current state."""
        try:
            return self.__state
        except Exception as err:
            log.error('state is undefined')
            raise KeyError('state is undefined') from err

    @property
    def states(self) -> Tuple['State', ...]:
        """Return list of states."""
        return tuple(self.superstate.substates.values())

    def get_state(self, statepath: str) -> 'State':
        """Get state from query path."""
        log.info("lookup state at path '%s'", statepath)
        subpaths = statepath.split('.')
        current = self.state if statepath.startswith('.') else self.__root
        for i, state in enumerate(subpaths):
            # if current != state:
            if current != state and isinstance(current, CompoundState):
                current = current.substates[state]
            if i == (len(subpaths) - 1):
                log.info("found state %s", current)
                return current
        raise InvalidState(f"state could not be found: {statepath}")

    def change_state(self, statepath: str) -> None:
        """Change current state to target state."""
        log.info('changing state from %s', statepath)
        self.state.run_on_exit(self)
        self.__state = self.get_state(statepath)
        self.state.run_on_entry(self)
        log.info('changed state to %s', statepath)

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

    def transition(self, event: str, *args, **kwargs: Any) -> Any:
        """Transition from event to target state."""
        statepath = kwargs.get('statepath')
        state = self.get_state(statepath) if statepath else self.state
        if hasattr(state, 'transitions'):
            for transition in state.transitions:
                if transition.event == event:
                    log.info("transitioning to '%s'", event)
                    return transition.callback()(self, *args, **kwargs)
        raise InvalidTransition("transition '%s' not found", event)

    def process_transitions(
        self, event: str, *args: Any, **kwargs: Any
    ) -> None:
        """Process transitions of a state change."""
        statepath = kwargs.get('statepath')
        state = self.get_state(statepath) if statepath else self.state
        _transitions = (
            state.get_transition(event)
            if hasattr(state, 'get_transition')
            else []
        )
        if _transitions == []:
            raise InvalidTransition('no transitions match event')
        _transition = self.__evaluate_guards(_transitions, *args, **kwargs)
        _transition.run(self, *args, **kwargs)
        log.info("processed transition event '%s'", _transition.event)

    def __evaluate_guards(
        self, transitions: Tuple['Transition', ...], *args: Any, **kwargs: Any
    ) -> 'Transition':
        allowed = []
        for _transition in transitions:
            if _transition.evaluate(self, *args, **kwargs):
                allowed.append(_transition)
        if len(allowed) == 0:
            raise GuardNotSatisfied('no transition possible from state')
        if len(allowed) > 1:
            raise ForkedTransition(
                'More than one transition was allowed for this event'
            )
        log.info("processed guard fo '%s'", allowed[0].event)
        return allowed[0]
