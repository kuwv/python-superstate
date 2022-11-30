"""Provide superstate core statechart capability."""

import logging
from copy import deepcopy
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Optional,
    Tuple,
    Union,
)

from superstate.exception import (
    InvalidConfig,
    InvalidState,
    InvalidTransition,
    ForkedTransition,
    GuardNotSatisfied,
)
from superstate.state import CompositeState, CompoundState, ParallelState

if TYPE_CHECKING:
    from superstate.state import State
    from superstate.transition import Transition
    from superstate.types import InitialType

log = logging.getLogger(__name__)


class MetaStateChart(type):
    """Instantiate statecharts from class metadata."""

    _root: 'State'

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

    __slots__ = ['__states', '__dict__']

    def __init__(
        self,
        initial: Optional[Union[Callable, str]] = None,
        **kwargs: Any,
    ) -> None:
        if 'logging_enabled' in kwargs and kwargs['logging_enabled']:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter(
                    fmt=' %(name)s :: %(levelname)-8s :: %(message)s'
                )
            )
            log.addHandler(handler)
            if 'logging_level' in kwargs:
                log.setLevel(kwargs['logging_level'].upper())
        log.info('initializing statemachine')

        # self.__traverse_states = kwargs.get('traverse_states', False)

        if hasattr(self.__class__, '_root'):
            self.__state = self.__superstate = self.__root = deepcopy(
                self.__class__._root
            )
        else:
            raise InvalidConfig(
                'attempted initialization with empty superstate'
            )

        if not initial and isinstance(self.superstate, CompoundState):
            initial = self.supertate.initial
        self.__process_initial(initial)
        log.info('loaded states and transitions')

        if kwargs.get('enable_start_transition', True):
            self.__state._run_on_entry(self)
            if self.state.kind == 'compound':
                self.__process_transient_state()
        log.info('statemachine initialization complete')

    def __getattr__(self, name: str) -> Any:
        if name.startswith('__'):
            raise AttributeError

        if name.startswith('is_'):
            if self.state.kind == 'parallel':
                for state in self.states:
                    if state.name == name[3:]:
                        return True
            return self.state.name == name[3:]

        # for key in list(self.states):
        #     if key == name:
        #         return self.__items[name]

        if self.state.kind == 'final':
            raise InvalidTransition('final state cannot transition')

        for transition in self.transitions:
            if transition.event == name or (
                transition.event == '' and name == '_auto_'
            ):
                return transition.callback().__get__(self, self.__class__)
        raise AttributeError

    @property
    def initial(self) -> Optional['InitialType']:
        """Provide current initial state from superstate."""
        return (
            self.superstate.initial
            if isinstance(self.superstate, CompoundState)
            else None
        )

    @property
    def transitions(self) -> Tuple['Transition', ...]:
        """Return list of current transitions."""
        # return self.state.transitions
        return tuple(
            self.state.transitions + self.superstate.transitions
            if self.state != self.superstate
            and isinstance(self.state, CompositeState)
            else self.superstate.transitions
        )

    @property
    def superstate(self) -> CompositeState:
        """Return superstate."""
        return self.__superstate

    @property
    def states(self) -> Tuple['State', ...]:
        """Return list of states."""
        return tuple(self.superstate.substates.values())

    @property
    def state(self) -> 'State':
        """Return the current state."""
        try:
            return self.__state
        except Exception as err:
            log.error('state is undefined')
            raise KeyError('state is undefined') from err

    def get_state(self, statepath: str) -> 'State':
        """Get state from query path."""
        subpaths = statepath.split('.')
        current = self.state if statepath.startswith('.') else self.__root
        for i, state in enumerate(subpaths):
            if current != state and isinstance(current, CompositeState):
                current = current.substates[state]
            if i == (len(subpaths) - 1):
                log.info("found state '%s'", current.name)
                return current
        raise InvalidState(f"state could not be found: {statepath}")

    def change_state(self, state: str) -> None:
        """Change current state to target state."""
        log.info('changing state from %s', state)
        # XXX: might not want target selection to be callable
        # state = state(self) if callable(state) else state
        superstate_path = state.split('.')[:-1]
        superstate = (
            self.get_state('.'.join(superstate_path))
            if superstate_path != []
            else self.__root
        )
        if isinstance(superstate, CompositeState):
            self.__superstate = superstate
        log.info("superstate is now '%s'", self.superstate)

        if isinstance(self.state, CompositeState):
            for substate in reversed(self.state.substates.values()):
                substate._run_on_exit(self)
        log.info("running on-exit tasks for state '%s'", state)
        self.state._run_on_exit(self)

        self.__state = self.get_state(state)
        log.info('state is now: %s', state)

        log.info("running on-entry tasks for state: '%s'", state)
        self.state._run_on_entry(self)

        if isinstance(self.state, CompositeState):
            self.__superstate = self.state
            if isinstance(self.state, CompoundState):
                self.__process_initial(self.state.initial)
            elif isinstance(self.state, ParallelState):
                # TODO: is this a better usecase for MP?
                for substate in self.state.substates.values():
                    substate._run_on_entry(self)
        self.__process_transient_state()
        log.info('changed state to %s', state)

    def transition(self, event: str, statepath: Optional[str] = None) -> Any:
        """Transition from event to target state."""
        state = self.get_state(statepath) if statepath else self.state
        if isinstance(state, CompositeState):
            for transition in state.transitions:
                if transition.event == event:
                    print('here', transition.event)
                    # return transition.callback().__get__(
                    #     self, self.__class__
                    # )
                    return transition.callback()
            raise AttributeError
        raise InvalidTransition('transition cannot be done from %s', state)

    def add_state(
        self, state: 'State', statepath: Optional[str] = None
    ) -> None:
        """Add state to either superstate or target state."""
        parent = self.get_state(statepath) if statepath else self.superstate
        if isinstance(parent, CompositeState):
            parent.add_state(state)
            log.info('added state %s', state.name)

    def add_transition(
        self, transition: 'Transition', statepath: Optional[str] = None
    ) -> None:
        """Add transition to either superstate or target state."""
        target = self.get_state(statepath) if statepath else self.superstate
        if isinstance(target, CompositeState):
            target.add_transition(transition)
            log.info('added transition %s', transition.event)
        # else:
        #     raise InvalidState(
        #         'cannot add transition to %s as %s state',
        #         target,
        #         target.kind
        #     )

    def _process_transitions(
        self, event: str, *args: Any, **kwargs: Any
    ) -> None:
        # TODO: need to consider superstate transitions.
        if isinstance(self.state, CompositeState):
            _transitions = self.state.get_transition(event)
            # _transitions += self.superstate.get_transition(event)
            if _transitions == []:
                raise InvalidTransition('no transitions match event')
            _transition = self.__evaluate_guards(_transitions, *args, **kwargs)
            _transition.run(self, *args, **kwargs)
            log.info("processed transition event '%s'", _transition.event)

    def __process_initial(
        self, initial: Optional['InitialType'] = None
    ) -> None:
        # TODO: process history state if defined
        if isinstance(self.superstate, CompoundState):
            if initial:
                _initial = initial(self) if callable(initial) else initial
                self.__state = self.get_state(_initial)
            elif not self.initial:
                raise InvalidConfig(
                    'an initial state must exist for statechart'
                )

    def __process_transient_state(self) -> None:
        if isinstance(self.state, CompositeState):
            for transition in self.state.transitions:
                if transition.event == '':
                    self._auto_()
                    break

    def __evaluate_guards(
        self, transitions: Tuple['Transition', ...], *args: Any, **kwargs: Any
    ) -> 'Transition':
        allowed = []
        for _transition in transitions:
            if _transition.evaluate(self, *args, **kwargs):
                allowed.append(_transition)
        if len(allowed) == 0:
            raise GuardNotSatisfied(
                'Guard is not satisfied for this transition'
            )
        if len(allowed) > 1:
            raise ForkedTransition(
                'More than one transition was allowed for this event'
            )
        log.info("processed guard fo '%s'", allowed[0].event)
        return allowed[0]
