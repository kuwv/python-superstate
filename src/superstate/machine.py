"""Provide parent core statechart capability."""

import logging
import os
from copy import deepcopy
from itertools import zip_longest
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
    cast,
)
from uuid import UUID

from superstate import config, construct
from superstate.exception import (
    InvalidConfig,
    InvalidState,
    InvalidTransition,
    GuardNotSatisfied,
)
from superstate.model import Null
from superstate.state import (
    AtomicState,
    CompositeState,
    # CompoundState,
    ParallelState,
)
from superstate.types import Binding

if TYPE_CHECKING:
    from superstate.model import DataModel
    from superstate.state import State
    from superstate.transition import Transition

log = logging.getLogger(__name__)


class MetaStateChart(type):
    """Instantiate statecharts from class metadata."""

    _name: str
    _initial: Union[Callable, 'State', str]
    _datamodel: str
    _root: 'CompositeState'
    _binding: str = cast(str, Binding('early', 'late'))

    def __new__(
        cls,
        name: str,
        bases: Tuple[type, ...],
        attrs: Dict[str, Any],
    ) -> 'MetaStateChart':
        name = attrs.pop('__name__', name.lower())
        initial = attrs.pop('__initial__', None)
        binding = attrs.pop('__binding__', config.DEFAULT_BINDING)
        # [early, late]
        # if binding != construct.DEFAULT_BINDING:
        #     construct.DEFAULT_BINDING = binding
        datamodel = attrs.pop('__datamodel__', config.DEFAULT_DATAMODEL)
        if datamodel != construct.DEFAULT_DATAMODEL:
            construct.DEFAULT_DATAMODEL = datamodel
        state = (
            construct.state(attrs.pop('__state__'))
            if '__state__' in attrs
            else None
        )
        obj = super().__new__(cls, name, bases, attrs)
        obj._name = name
        obj._initial = initial
        obj._binding = binding
        cls._datamodel = datamodel
        if state:
            obj._root = state  # type: ignore
        return obj


class StateChart(metaclass=MetaStateChart):
    """Represent statechart capabilities."""

    # __slots__ = ['__root', '__state', '__parent', '__dict__', 'initial']
    __root: 'CompositeState'
    __state: 'State'
    __parent: 'CompositeState'
    _initial: Union[Callable, 'State', str]

    # # System Variables
    # _name: str
    # _event: Event
    # _sessionid: str
    # _ioprocessors: Iterable[IOProcessor]
    # _x: Optional['DataModel'] = None

    # TODO: support crud operations through mixin and __new__
    # TODO: crud taxonomy='dynamic' or mutable Optional[bool]

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

        self._sessionid = UUID(
            bytes=os.urandom(16), version=4  # pylint: disable=no-member
        )

        if hasattr(self.__class__, '_root'):
            self.__root = deepcopy(self.__class__._root)
        elif 'parent' in kwargs:
            self.__root = deepcopy(kwargs['parent'])
        else:
            raise InvalidConfig('attempted initialization with empty parent')
        self.__state = self.__root

        # initial setup
        if not self._initial:
            self._initial = kwargs.get(
                'initial',
                self.root.initial if hasattr(self.root, 'initial') else None,
            )
        self.state._process_transient_state(self)  # type: ignore
        if self.root == self.state:
            initial = (
                self.initial(self) if callable(self.initial) else self.initial
            )
            if initial:
                self.__state = self.get_state(initial)
            elif not isinstance(self.__root, ParallelState):
                raise InvalidConfig(
                    'an initial state must exist for statechart'
                )
        log.info('loaded states and transitions')

        # self.parent.run_on_entry(self)
        self.state.run_on_entry(self)
        log.info('statechart initialization complete')
        self._root = None

    def __getattr__(self, name: str) -> Any:
        # do not attempt to resolve missing dunders
        if name.startswith('__'):
            raise AttributeError

        # handle state check locally
        if name.startswith('is_'):
            return name[3:] in self.active

        # handle automatic transitions
        if name == '_auto_':

            def wrapper(*args: Any, **kwargs: Any) -> Optional[Any]:
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

        # retrieve child by name
        for key in list(self.states):
            if key == name:
                return self.parent.states[name]
        raise AttributeError

    @property
    def datamodel(self) -> 'DataModel':
        """Return the active datamodel type."""
        return self.root.datamodel if self.root.datamodel else Null()

    @property
    def initial(self) -> Union[Callable, 'State', str]:
        """Return initial state of current parent."""
        return self._initial

    @property
    def root(self) -> 'CompositeState':
        """Return root state of statechart."""
        return self.__root

    @property
    def parent(self) -> 'CompositeState':
        """Return parent."""
        return self.state.parent or self.root

    @property
    def state(self) -> 'State':
        """Return the current state."""
        return self.__state

    @property
    def states(self) -> Tuple['State', ...]:
        """Return list of states."""
        return tuple(self.parent.states.values())

    @property
    def active(self) -> Tuple['State', ...]:
        """Return active states."""
        states: List['State'] = []
        parents = list(reversed(self.state))  # type: ignore
        for i, x in enumerate(parents):
            n = i + 1
            if not n >= len(parents) and isinstance(parents[n], ParallelState):
                states += list((parents[n]).states)
            else:
                states.append(x)
        return tuple(states)

    def get_relpath(self, target: str) -> str:
        """Get relative statepath of target state to current state."""
        if self.state == target:
            relpath = '.'
        else:
            path = ['']
            source_path = self.state.path.split('.')
            target_path = self.get_state(target).path.split('.')
            for i, x in enumerate(
                zip_longest(source_path, target_path, fillvalue='')
            ):
                if x[0] != x[1]:
                    if x[0] != '':
                        path.extend(['' for x in source_path[i:]])
                    if x[1] != '':
                        path.extend(target_path[i:])
                    if i == 0:
                        raise Exception(
                            f"no relative path exists for: {target!s}"
                        )
                    break
            relpath = '.'.join(path)
        return relpath

    def change_state(self, statepath: str) -> None:
        """Traverse statepath."""
        relpath = self.get_relpath(statepath)
        if relpath == '.':
            self.state.run_on_exit(self)
            self.state.run_on_entry(self)
        else:
            subpaths = relpath.split('.')
            size = len(subpaths) - 1
            for index, subpath in enumerate(subpaths):
                try:
                    if subpath == '':
                        if index == 0:
                            continue
                        self.state.run_on_exit(self)
                        self.__state = self.active[1]
                    elif (
                        isinstance(self.state, CompositeState)
                        and subpath in self.state.states.keys()
                    ):
                        state = self.state.states[subpath]
                        self.__state = state
                        state.run_on_entry(
                            self, enable_triggers=(index == size)
                        )
                    else:
                        raise Exception(f"path not found: {statepath}")
                except Exception as err:
                    log.error(err)
                    raise KeyError('parent is undefined') from err
        # if type(self.state) not in [AtomicState, ParallelState]:
        #     # TODO: need to transition from CompoundState to AtomicState
        #     print('state transition not complete')
        log.info('changed state to %s', statepath)

    def get_state(self, statepath: str) -> 'State':
        """Get state."""
        subpaths = statepath.split('.')
        state: 'State' = self.root

        # general recursive search for single query
        if len(subpaths) == 1 and isinstance(state, CompositeState):
            for x in list(state):
                if x == subpaths[0]:
                    return x
        # set start point for relative lookups
        elif statepath.startswith('.'):
            relative = len(statepath) - len(statepath.lstrip('.')) - 1
            state = self.active[relative:][0]
            rel = relative + 1
            subpaths = [state.name] + subpaths[rel:]

        # check relative lookup is done
        target = subpaths[-1]
        if target in ('', state):
            return state

        # path based search
        while state and subpaths:
            subpath = subpaths.pop(0)
            # skip if current state is at subpath
            if state == subpath:
                continue
            # return current state if target found
            if state == target:
                return state
            # walk path if exists
            if hasattr(state, 'states') and subpath in state.states.keys():
                state = state.states[subpath]
                # check if target is found
                if not subpaths:
                    return state
            else:
                break
        raise InvalidState(f"state could not be found: {statepath}")

    def add_state(
        self, state: 'State', statepath: Optional[str] = None
    ) -> None:
        """Add state to either parent or target state."""
        parent = self.get_state(statepath) if statepath else self.parent
        if isinstance(parent, CompositeState):
            parent.add_state(state)
            log.info('added state %s', state.name)
        else:
            raise InvalidState(
                f"cannot add state to non-composite state {parent.name}"
            )

    @property
    def transitions(self) -> Tuple['Transition', ...]:
        """Return list of current transitions."""
        return (
            tuple(self.state.transitions)
            if hasattr(self.state, 'transitions')
            else ()
        )

    def add_transition(
        self, transition: 'Transition', statepath: Optional[str] = None
    ) -> None:
        """Add transition to either parent or target state."""
        target = self.get_state(statepath) if statepath else self.parent
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
            else []
        )

    def process_transitions(
        self, event: str, /, *args: Any, **kwargs: Any
    ) -> 'Transition':
        """Get transition event from active states."""
        # TODO: must use datamodel to process transitions
        # child => parent => grandparent
        guarded: List['Transition'] = []
        for current in self.active:
            transitions: List['Transition'] = []

            # search parallel states for transitions
            if isinstance(current, ParallelState):
                for state in current.states.values():
                    transitions += self._lookup_transitions(event, state)
            else:
                transitions = self._lookup_transitions(event, current)

            # evaluate guards
            allowed = [
                t for t in transitions if t.evaluate(self, *args, **kwargs)
            ]
            if allowed:
                # if len(allowed) > 1:
                #     raise InvalidConfig(
                #         'Conflicting transitions were allowed for event',
                #         event
                #     )
                return allowed[0]
            guarded += transitions
        if len(guarded) != 0:
            raise GuardNotSatisfied('no transition possible from state')
        raise InvalidTransition(f"transition could not be found: {event}")

    def trigger(
        self, event: str, /, *args: Any, **kwargs: Any
    ) -> Optional[Any]:
        """Transition from event to target state."""
        # XXX: currently does not allow contional transient states
        transition = self.process_transitions(event, *args, **kwargs)
        if transition:
            log.info('transitioning to %r', event)
            result = transition(self, *args, **kwargs)
            return result
        raise InvalidTransition('transition %r not found', event)
