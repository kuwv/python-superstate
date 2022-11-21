# Copyright (c) 2022 Jesse P. Johnson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Compact statechart that can be vendored."""

import inspect
import logging
from copy import deepcopy
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
    # cast,
)

__author__ = 'Jesse P. Johnson'
__author_email__ = 'jpj6652@gmail.com'
__title__ = 'superstate'
__description__ = 'Compact statechart that can be vendored.'
__version__ = '1.1.0a3'
__license__ = 'MIT'
__copyright__ = 'Copyright 2022 Jesse Johnson.'
__all__ = (
    'StateChart',
    'State',
    'Transition',
    'states',
    'state',
    'transitions',
    'transition',
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

EventAction = Union[Callable, str]
EventActions = Union[EventAction, Iterable[EventAction]]
GuardCondition = Union[Callable, str]
GuardConditions = Union[GuardCondition, Iterable[GuardCondition]]
InitialType = Union[Callable, str]

STATE: Optional['State'] = None
# enable_signature_truncation = False


def transition(config: Union['Transition', dict]) -> 'Transition':
    if isinstance(config, Transition):
        return config
    if isinstance(config, dict):
        return Transition(
            event=config['event'],
            target=config['target'],
            action=config.get('action'),
            cond=config.get('cond'),
        )
    raise InvalidConfig('could not find a valid transition configuration')


def state(config: Union['State', dict, str]) -> 'State':
    if isinstance(config, State):
        return config
    elif isinstance(config, str):
        return State(config)
    elif isinstance(config, dict):
        cls = config.get('factory', State)
        return cls(
            name=config['name'],
            initial=config.get('initial'),
            kind=config.get('kind'),
            states=(
                states(*config['states'], update_global=False)
                if 'states' in config
                else []
            ),
            transitions=(
                transitions(*config['transitions'], update_global=False)
                if 'transitions' in config
                else []
            ),
            on_entry=config.get('on_entry'),
            on_exit=config.get('on_exit'),
        )
    raise InvalidConfig('could not find a valid state configuration')


def transitions(*args: Any, **kwargs: Any) -> List['Transition']:
    return list(map(transition, args))


def states(*args: Any, **kwargs: Any) -> List['State']:
    return list(map(state, args))


def create_machine(config: Dict[str, Any], **kwargs: Any) -> 'State':
    global STATE
    cls = kwargs.get('factory', State)
    _state = cls(
        name=config.get('name', 'root'),
        initial=config.get('initial'),
        kind=config.get('kind'),
        states=states(*config.get('states', [])),
        transitions=transitions(*config.get('transitions', [])),
        **kwargs,
    )
    STATE = _state
    return _state


def tuplize(value: Any) -> Tuple[Any, ...]:
    # TODO: tuplize if generator
    return tuple(value) if type(value) in (list, tuple) else (value,)


# class NameDescriptor:
#     def __get__(
#         self, obj: object, objtype: Optional[type[object]] = None
#     ) -> str:
#         return self.value
#
#     def __set__(self, obj: object, value: str) -> None:
#         if not value.replace('_', '').isalnum():
#             raise InvalidConfig('state name contains invalid characters')
#         self.value = value


class Action:
    __slots__ = ['__machine']

    def __init__(self, machine: 'StateChart') -> None:
        self.__machine = machine

    def run(
        self,
        params: EventActions,
        *args: Any,
        **kwargs: Any,
    ) -> Tuple[Any, ...]:
        return tuple(
            self._run_action(x, *args, **kwargs) for x in tuplize(params)
        )

    def _run_action(
        self, action: EventAction, *args: Any, **kwargs: Any
    ) -> Any:
        if callable(action):
            return self.__run_with_args(
                action, self.__machine, *args, **kwargs
            )
        return self.__run_with_args(
            getattr(self.__machine, action), *args, **kwargs
        )

    @staticmethod
    def __run_with_args(action: Callable, *args: Any, **kwargs: Any) -> Any:
        signature = inspect.signature(action)
        if len(signature.parameters.keys()) != 0:
            return action(*args, **kwargs)
        return action()


class Guard:
    __slots__ = ['__machine']

    def __init__(self, machine: 'StateChart') -> None:
        self.__machine = machine

    def evaluate(
        self, cond: GuardConditions, *args: Any, **kwargs: Any
    ) -> bool:
        result = True
        for x in tuplize(cond):
            result = result and self.__evaluate(x, *args, **kwargs)
            if result is False:
                break
        return result

    def __evaluate(
        self, cond: GuardCondition, *args: Any, **kwargs: Any
    ) -> bool:
        if callable(cond):
            return cond(self.__machine, *args, **kwargs)
        else:
            guard = getattr(self.__machine, cond)
            if callable(guard):
                return self.__evaluate_with_args(guard, *args, **kwargs)
            return bool(guard)

    @staticmethod
    def __evaluate_with_args(
        cond: Callable, *args: Any, **kwargs: Any
    ) -> bool:
        signature = inspect.signature(cond)
        params = dict(signature.parameters)

        if len(params.keys()) != 0:
            # _kwargs = {k: v for k, v in kwargs.items() if k in params.keys()}
            # _args = tuple(
            #     x
            #     for i, x in enumerate(params.keys())
            #     if i < (len(params.keys()) - len(_kwargs.keys()))
            # )
            return cond(*args, **kwargs)
        return cond()


class Transition:
    __slots__ = ['event', 'target', 'action', 'cond']
    # event = cast(str, NameDescriptor())
    # target = cast(str, NameDescriptor())

    def __init__(
        self,
        event: str,
        target: str,
        action: Optional[EventActions] = None,
        cond: Optional[GuardConditions] = None,
    ) -> None:
        self.event = event
        self.target = target
        self.action = action
        self.cond = cond

    def __repr__(self) -> str:
        return repr(f"Transition(event={self.event}, target={self.target})")

    def callback(self) -> Callable:
        def event(machine: 'StateChart', *args: Any, **kwargs: Any) -> None:
            machine._process_transitions(self.event, *args, **kwargs)

        event.__name__ = self.event
        event.__doc__ = f"Show event: '{self.event}'."
        return event

    def evaluate(
        self, machine: 'StateChart', *args: Any, **kwargs: Any
    ) -> bool:
        return (
            Guard(machine).evaluate(self.cond, *args, **kwargs)
            if self.cond
            else True
        )

    def run(self, machine: 'StateChart', *args: Any, **kwargs: Any) -> None:
        machine._change_state(self.target)
        if self.action:
            Action(machine).run(self.action, *args, **kwargs)
            log.info(f"executed action event for '{self.event}'")
        else:
            log.info(f"no action event for '{self.event}'")


class State:
    __slots__ = [
        'name',
        '__initial',
        '__state',
        '__states',
        '__transitions',
        '__on_entry',
        '__on_exit',
        '__kind',
        '__dict__',
    ]
    # name = cast(str, NameDescriptor())
    __initial: Optional[InitialType]
    __on_entry: Optional[EventActions]
    __on_exit: Optional[EventActions]

    def __init__(
        self,
        name: str,
        transitions: List['Transition'] = [],
        states: List['State'] = [],
        **kwargs: Any,
    ) -> None:
        if not name.replace('_', '').isalnum():
            raise InvalidConfig('state name contains invalid characters')
        self.name = name
        self.__kind = kwargs.get('kind')

        self.__state = self
        self.__states = {x.name: x for x in states}
        # self.__states = {x.name: x for x in args if isinstance(x, State)}

        self.__transitions = transitions
        # self.__transitions = [x for x in args if isinstance(x, Transition)]
        for x in self.transitions:
            self.__register_transition_callback(x)

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
        elif isinstance(other, str):
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
            if len(self.__states) < 2:
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
    def initial(self) -> Optional[InitialType]:
        """Return initial substate if defined."""
        return self.__initial

    @property
    def kind(self) -> str:
        """Return state type."""
        if self.__kind:
            kind = self.__kind
        elif self.substates != {} and self.transitions != []:
            for x in self.transitions:
                if x == '':
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
        return self.__state

    @property
    def substates(self) -> Dict[str, 'State']:
        """Return substates."""
        return self.__states

    @property
    def transitions(self) -> Tuple['Transition', ...]:
        """Return transitions of this state."""
        return tuple(self.__transitions)

    def add_state(self, state: 'State') -> None:
        """Add substate to this state."""
        self.__states[state.name] = state

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
        if self.__on_entry is not None:
            Action(machine).run(self.__on_entry)
            log.info(
                f"executed 'on_entry' state change action for {self.name}"
            )

    def _run_on_exit(self, machine: 'StateChart') -> None:
        if self.__on_exit is not None:
            Action(machine).run(self.__on_exit)
            log.info(f"executed 'on_exit' state change action for {self.name}")


class MetaStateChart(type):
    _root: 'State'

    def __new__(
        cls,
        name: str,
        bases: Tuple[type, ...],
        attrs: Dict[str, Any],
    ) -> 'MetaStateChart':
        global STATE
        obj = super(MetaStateChart, cls).__new__(cls, name, bases, attrs)
        if STATE:
            obj._root = STATE
        STATE = None
        return obj


class StateChart(metaclass=MetaStateChart):
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

        self.__process_initial(initial or self.superstate.initial)
        log.info('loaded states and transitions')

        if kwargs.get('enable_start_transition', True):
            self.__state._run_on_entry(self)
            self.__process_transient_state()
        log.info('statemachine initialization complete')

    def __getattr__(self, name: str) -> Any:
        if name.startswith('__'):
            raise AttributeError

        if name.startswith('is_'):
            if self.state.kind == 'parallel':
                for s in self.states:
                    if s.name == name[3:]:
                        return True
            return self.state.name == name[3:]

        # for key in list(self.states):
        #     if key == name:
        #         return self.__items[name]

        if self.state.kind == 'final':
            raise InvalidTransition('final state cannot transition')

        for t in self.transitions:
            if t.event == name or (t.event == '' and name == '_auto_'):
                return t.callback().__get__(self, self.__class__)
        raise AttributeError

    @property
    def initial(self) -> Optional[InitialType]:
        return self.superstate.initial

    @property
    def transitions(self) -> Tuple['Transition', ...]:
        """Return list of current transitions."""
        # return self.state.transitions
        return tuple(
            self.state.transitions + self.superstate.transitions
            if self.state != self.superstate
            else self.state.transitions
        )

    @property
    def superstate(self) -> 'State':
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
        except Exception:
            log.error('state is undefined')
            raise KeyError

    def get_state(self, statepath: str) -> 'State':
        """Get state from query path."""
        subpaths = statepath.split('.')
        current = self.state if statepath.startswith('.') else self.__root
        for i, state in enumerate(subpaths):
            if current != state:
                current = current.substates[state]
            if i == (len(subpaths) - 1):
                log.info(f"found state '{current.name}'")
                return current
        raise InvalidState(f"state could not be found: {statepath}")

    def _change_state(self, state: str) -> None:
        """Change current state to target state."""
        log.info(f"changing state from {state}")
        # XXX: might not want target selection to be callable
        state = state(self) if callable(state) else state
        superstate = state.split('.')[:-1]
        self.__supertstate = (
            self.get_state('.'.join(superstate))
            if superstate != []
            else self.__root
        )
        # if self.state.kind != 'parallel': iterate run_on_exit()
        self.state._run_on_exit(self)
        self.__state = self.get_state(state)
        self.state._run_on_entry(self)
        if self.state.kind == 'compound' or self.state.kind == 'parallel':
            self.__superstate = self.state
            if self.state.kind == 'compound':
                self.__process_initial(self.state.initial)
            if self.state.kind == 'parallel':
                # TODO: is this a better usecase for MP?
                for x in self.state.substates.values():
                    x._run_on_entry(self)
        self.__process_transient_state()
        log.info(f"changed state to {state}")

    def transition(self, event: str, statepath: Optional[str] = None) -> None:
        state = self.get_state(statepath) if statepath else self.state
        for t in state.transitions:
            if t.event == event:
                return t.callback().__get__(self, self.__class__)

    def add_state(
        self, state: 'State', statepath: Optional[str] = None
    ) -> None:
        """Add state to either superstate or target state."""
        parent = self.get_state(statepath) if statepath else self.superstate
        parent.add_state(state)
        log.info(f"added state {state.name}")

    def add_transition(
        self, transition: 'Transition', statepath: Optional[str] = None
    ) -> None:
        """Add transition to either superstate or target state."""
        target = self.get_state(statepath) if statepath else self.superstate
        target.add_transition(transition)
        log.info(f"added transition {transition.event}")

    def _process_transitions(
        self, event: str, *args: Any, **kwargs: Any
    ) -> None:
        # TODO: need to consider superstate transitions.
        _transitions = self.state.get_transition(event)
        # _transitions += self.superstate.get_transition(event)
        if _transitions == []:
            raise InvalidTransition('no transitions match event')
        _transition = self.__evaluate_guards(_transitions, *args, **kwargs)
        _transition.run(self, *args, **kwargs)
        log.info(f"processed transition event '{_transition.event}'")

    def __process_initial(self, initial: Optional[InitialType] = None) -> None:
        if initial:
            _initial = initial(self) if callable(initial) else initial
            self.__state = self.get_state(_initial)
        elif self.superstate.kind != 'parallel' and not self.initial:
            raise InvalidConfig('an initial state must exist for statechart')

    def __process_transient_state(self) -> None:
        for x in self.state.transitions:
            if x.event == '':
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
        elif len(allowed) > 1:
            raise ForkedTransition(
                'More than one transition was allowed for this event'
            )
        log.info(f"processed guard fo '{allowed[0].event}'")
        return allowed[0]


class FluidstateException(Exception):
    pass


class InvalidConfig(FluidstateException):
    pass


class InvalidTransition(FluidstateException):
    pass


class InvalidState(FluidstateException):
    pass


class GuardNotSatisfied(FluidstateException):
    pass


class ForkedTransition(FluidstateException):
    pass
