"""Provide parent core statechart capability."""

from __future__ import annotations

import logging
import logging.config
import os
from copy import deepcopy
from itertools import zip_longest
from typing import TYPE_CHECKING, Any, Iterator, Optional, cast
from uuid import UUID

from superstate.config import DEFAULT_BINDING, DEFAULT_PROVIDER
from superstate.exception import (
    ConditionNotSatisfied,
    InvalidConfig,
    InvalidPath,
    InvalidState,
    InvalidTransition,
)
from superstate.model.data import DataModel
from superstate.provider import PROVIDERS
from superstate.state import (
    AtomicState,
    # CompoundState,
    ParallelState,
    State,
    SubstateMixin,
)
from superstate.types import Selection

if TYPE_CHECKING:
    # from superstate.model.data import Data
    from superstate.transition import Transition
    from superstate.types import Initial

log = logging.getLogger(__name__)


class MetaStateChart(type):
    """Instantiate statecharts from class metadata."""

    __name__: str
    __initial__: Initial
    __binding__: str = cast(str, Selection('early', 'late'))
    __datamodel__: str
    _root: SubstateMixin
    datamodel: DataModel

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        attrs: dict[str, Any],
    ) -> 'MetaStateChart':
        if '__name__' not in attrs:
            name = name.lower()
            attrs['__name__'] = name
        else:
            name = attrs.get('__name__', name.lower())

        initial = attrs.get('__initial__', None)
        root = State.create(attrs.pop('state')) if 'state' in attrs else None

        # setup datamodel
        binding = attrs.get('__binding__', DEFAULT_BINDING)
        if binding:
            DataModel.binding = binding
        provider = attrs.get('__datamodel__', DEFAULT_PROVIDER)
        if provider != DEFAULT_PROVIDER:
            DataModel.provider = PROVIDERS[provider]
        datamodel = DataModel.create(attrs.pop('datamodel', {'data': []}))
        # XXX: chaining datamodels not working
        # datamodel['data'].append({'id': 'root', 'expr': root})

        obj = super().__new__(mcs, name, bases, attrs)
        obj.__name__ = name
        obj.__initial__ = initial
        obj.__binding__ = binding
        obj.__datamodel__ = provider
        obj.datamodel = datamodel
        if root:
            obj._root = root  # type: ignore
        return obj


class StateChart(metaclass=MetaStateChart):
    """Represent statechart capabilities."""

    #     The configuration contains exactly one child of the <scxml> element.
    #     The configuration contains one or more atomic states.
    #     When the configuration contains an atomic state, it contains all of
    #         its <state> and <parallel> ancestors.
    #     When the configuration contains a non-atomic <state>, it contains one
    #         and only one of the state's states.
    #     If the configuration contains a <parallel> state, it contains all of
    #         its states.

    # __slots__ = [
    #     '__dict__', '__current_state', '__parent', '__root', 'initial'
    # ]
    __root: SubstateMixin
    __parent: SubstateMixin
    __current_state: State

    # # System Variables
    # _name: str
    # _event: Event
    # _sessionid: str
    # _ioprocessors: Sequence[IOProcessor]
    # _x: Optional['DataModel'] = None

    # TODO: support crud operations through mixin and __new__
    # TODO: crud taxonomy='dynamic' or mutable Optional[bool]

    def __init__(
        self,
        # *args: Any,
        **kwargs: Any,
    ) -> None:
        if 'logging_enabled' in kwargs and kwargs['logging_enabled']:
            if 'logging_level' in kwargs:
                log.setLevel(kwargs.pop('logging_level').upper())
        log.info('initializing statechart')

        self._sessionid = UUID(
            bytes=os.urandom(16),
            version=4,  # pylint: disable=no-member
        )

        self.datamodel.populate()

        if hasattr(self.__class__, '_root'):
            self.__root = deepcopy(self.__class__._root)
            self._root = None
        elif 'superstate' in kwargs:
            self.__root = kwargs.pop('superstate')
        else:
            raise InvalidConfig('attempted initialization with empty parent')

        self.__current_state = self.__root
        if not isinstance(self.__root, ParallelState):
            self.__initial__: Optional[str] = kwargs.get(
                'initial', self.__initial__
            )
            if self.initial:
                self.__current_state = self.get_state(
                    self.initial
                    # self.initial.transition.target
                )
        log.info('loaded states and transitions')

        # XXX: require composite state
        self.current_state.run_on_entry(self)
        log.info('statechart initialization complete')

        # XXX: need to process after initial state
        # if isinstance(self.current_state, AtomicState):
        #     self.current_state._process_transient_state(self)

    def __getattr__(self, name: str) -> Any:
        # do not attempt to resolve missing dunders
        if name.startswith('__'):
            raise AttributeError
        # handle state check for active states
        if name.startswith('is_'):
            return name[3:] in self.active
        raise AttributeError(f"cannot find attribute: {name}")

    @property
    def initial(self) -> Optional[str]:
        """Return initial state of current parent."""
        if self.__initial__ is None:
            if hasattr(self.root, 'initial'):
                self.__initial__ = self.root.initial
            elif self.root.states:
                self.__initial__ = list(self.root.states.values())[0].name
            else:
                self.__initial__ = None
        return self.__initial__

    @property
    def current_state(self) -> State:
        """Return the current state."""
        # TODO: rename to head or position potentially
        return self.__current_state

    @current_state.setter
    def current_state(self, state: State) -> None:
        """Set the current state."""
        if hasattr(self.current_state, 'states'):
            if state in list(self.current_state.states.values()):
                self.__current_state = state
                return
        if len(self.active) > 1 and self.active[1] == state:
            self.__current_state = state
        else:
            raise InvalidTransition('cannot transition from final state')

    @property
    def root(self) -> SubstateMixin:
        """Return root state of statechart."""
        return self.__root

    @property
    def parent(self) -> SubstateMixin:
        """Return parent."""
        return self.current_state.parent or self.root

    @property
    def children(self) -> tuple[State, ...]:
        """Return list of states."""
        return (
            tuple(self.__current_state.states.values())
            if hasattr(self.__current_state, 'states')
            else ()
        )

    @property
    def states(self) -> tuple[State, ...]:
        """Return list of states."""
        return tuple(self.parent.states.values())

    @property
    def siblings(self) -> tuple[State, ...]:
        """Return list of states."""
        return tuple(self.parent.states.values())

    @property
    def active(self) -> tuple[State, ...]:
        """Return active states."""
        states: list[State] = []
        parents = list(reversed(self.current_state))
        for i, x in enumerate(parents):
            n = i + 1
            if not n >= len(parents) and isinstance(parents[n], ParallelState):
                states += list((parents[n]).states)  # type: ignore
            else:
                states.append(x)
        return tuple(states)

    def get_relpath(self, target: str) -> str:
        """Get relative statepath of target state to current state."""
        if target in ('', self.current_state):  # self reference
            relpath = '.'
        else:
            path = ['']
            source_path = self.current_state.path.split('.')
            target_path = self.get_state(target).path.split('.')
            for i, x in enumerate(
                zip_longest(source_path, target_path, fillvalue='')
            ):
                if x[0] != x[1]:
                    if x[0] != '':  # target is a descendent
                        path.extend(['' for x in source_path[i:]])
                    if x[1] == '':  # target is a ascendent
                        path.extend([''])
                    if x[1] != '':  # target is child of a ascendent
                        path.extend(target_path[i:])
                    if i == 0:
                        raise InvalidPath(
                            f"no relative path exists for: {target!s}"
                        )
                    break
            relpath = '.'.join(path)
        return relpath

    def change_state(self, statepath: str) -> None:
        """Traverse statepath."""
        relpath = self.get_relpath(statepath)
        if relpath == '.':  # handle self transition
            self.current_state.run_on_exit(self)
            self.current_state.run_on_entry(self)
        else:
            s = 2 if relpath.endswith('.') else 1  # stupid black
            macrostep = relpath.split('.')[s:]
            for microstep in macrostep:
                try:
                    if microstep == '':  # reverse
                        self.current_state.run_on_exit(self)
                        self.__current_state = self.active[1]
                    elif (
                        isinstance(self.current_state, SubstateMixin)
                        and microstep in self.current_state.states.keys()
                    ):  # forward
                        state = self.current_state.states[microstep]
                        self.__current_state = state
                        state.run_on_entry(self)
                    else:
                        raise InvalidPath(f"statepath not found: {statepath}")
                except Exception as err:
                    log.error(err)
                    raise KeyError('parent is undefined') from err
        # if type(self.current_state) not in [AtomicState, ParallelState]:
        #     # TODO: need to transition from CompoundState to AtomicState
        #     print('state transition not complete')
        log.info('changed state to %s', statepath)

    def get_state(self, statepath: str) -> State:
        """Get state."""
        state: State = self.root
        macrostep = statepath.split('.')

        # general recursive search for single query
        if len(macrostep) == 1 and isinstance(state, SubstateMixin):
            for x in list(state):
                if x == macrostep[0]:
                    return x
        # set start point for relative lookups
        elif statepath.startswith('.'):
            relative = len(statepath) - len(statepath.lstrip('.')) - 1
            state = self.active[relative:][0]
            rel = relative + 1
            macrostep = [state.name] + macrostep[rel:]

        # check relative lookup is done
        target = macrostep[-1]
        if target in ('', state):
            return state

        # path based search
        while state and macrostep:
            microstep = macrostep.pop(0)
            # skip if current state is at microstep
            if state == microstep:
                continue
            # return current state if target found
            if state == target:
                return state
            # walk path if exists
            if hasattr(state, 'states') and microstep in state.states.keys():
                state = state.states[microstep]
                # check if target is found
                if not macrostep:
                    return state
            else:
                break
        raise InvalidState(f"state could not be found: {statepath}")

    def add_state(self, state: State, statepath: Optional[str] = None) -> None:
        """Add state to either parent or target state."""
        parent = self.get_state(statepath) if statepath else self.parent
        if isinstance(parent, SubstateMixin):
            parent.add_state(state)
            log.info('added state %s', state.name)
        else:
            raise InvalidState(
                f"cannot add state to non-composite state {parent.name}"
            )

    @property
    def transitions(self) -> Iterator[Transition]:
        """Return list of current transitions."""
        for state in self.active:
            if hasattr(state, 'transitions'):
                yield from state.transitions
            else:
                continue

    def add_transition(
        self, transition: Transition, statepath: Optional[str] = None
    ) -> None:
        """Add transition to either parent or target state."""
        target = self.get_state(statepath) if statepath else self.parent
        if isinstance(target, AtomicState):
            target.add_transition(transition)
            log.info('added transition %s', transition.event)
        else:
            raise InvalidState('cannot add transition to %s', target)

    def get_transitions(self, event: str) -> tuple[Transition, ...]:
        """Get each transition maching event."""
        return tuple(filter(lambda t: t.event == event, self.transitions))

    def trigger(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        """Transition from event to target state."""
        # TODO: need to consider superstate transitions.
        if self.current_state.type == 'final':
            raise InvalidTransition('cannot transition from final state')

        transitions = self.get_transitions(event)
        if not transitions:
            raise InvalidTransition('no transitions match event')
        allowed = [t for t in transitions if t.evaluate(self, *args, **kwargs)]
        if not allowed:
            raise ConditionNotSatisfied(
                'Condition is not satisfied for this transition'
            )
        if len(allowed) > 1:
            raise InvalidTransition(
                'More than one transition was allowed for this event'
            )
        log.info('processed guard for %s', allowed[0].event)
        allowed[0].execute(self, *args, **kwargs)
        log.info('processed transition event %s', allowed[0].event)
