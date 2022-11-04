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

"""Compact state machine that can be vendored."""

import logging
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
__title__ = 'fluidstate'
__description__ = 'Compact statechart that can be vendored.'
__version__ = '1.1.0a1'
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

EventAction = Union[str, Callable]
EventActions = Union[EventAction, Iterable[EventAction]]
GuardCondition = Union[str, Callable]
GuardConditions = Union[GuardCondition, Iterable[GuardCondition]]
StateType = str
StateTypes = Union[StateType, Iterable[StateType]]

STATE: Optional['State'] = None


def transition(arg: Union['Transition', dict]) -> 'Transition':
    if isinstance(arg, Transition):
        return arg
    if isinstance(arg, dict):
        return Transition(
            event=arg['event'],
            target=arg['target'],
            action=arg.get('action'),
            cond=arg.get('cond'),
        )
    raise InvalidConfig('could not find a valid transition configuration')


def state(arg: Union['State', dict, str]) -> 'State':
    if isinstance(arg, State):
        return arg
    elif isinstance(arg, str):
        return State(arg)
    elif isinstance(arg, dict):
        return State(
            name=arg['name'],
            initial=arg.get('initial'),
            states=(
                states(*arg['states'], update_global=False)
                if 'states' in arg
                else []
            ),
            transitions=(
                transitions(*arg['transitions'], update_global=False)
                if 'transitions' in arg
                else []
            ),
            on_entry=arg.get('on_entry'),
            on_exit=arg.get('on_exit'),
        )
    raise InvalidConfig('could not find a valid state configuration')


def transitions(*args: Any, **kwargs: Any) -> List['Transition']:
    return list(map(transition, args))


def states(*args: Any, **kwargs: Any) -> List['State']:
    return list(map(state, args))


def create_machine(config: Dict[str, Any]) -> 'State':
    global STATE
    STATE = State(
        name=config.get('name', 'root'),
        initial=config.get('initial'),
        states=states(*config.get('states', [])),
        transitions=transitions(*config.get('transitions', [])),
        # **kwargs,
    )
    return STATE


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
    ) -> None:
        for x in tuplize(params):
            self._run_action(x, *args, **kwargs)

    def _run_action(
        self, action: EventAction, *args: Any, **kwargs: Any
    ) -> None:
        if callable(action):
            self.__run_with_args(action, self.__machine, *args, **kwargs)
        else:
            self.__run_with_args(
                getattr(self.__machine, action), *args, **kwargs
            )

    @staticmethod
    def __run_with_args(action: Callable, *args: Any, **kwargs: Any) -> None:
        try:
            action(*args, **kwargs)
        except TypeError:
            action()


class Guard:
    __slots__ = ['__machine']

    def __init__(self, machine: 'StateChart') -> None:
        self.__machine = machine

    def evaluate(self, cond: GuardConditions) -> bool:
        result = True
        for x in tuplize(cond):
            result = result and self.__evaluate(self.__machine, x)
        return result

    @staticmethod
    def __evaluate(machine: 'StateChart', cond: GuardCondition) -> bool:
        if callable(cond):
            return cond(machine)
        else:
            guard = getattr(machine, cond)
            if callable(guard):
                return guard()
            return guard


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
        # TODO: event needs to allow none for automatic transitions
        self.event = event
        self.target = target
        self.action = action
        self.cond = cond

    def __repr__(self) -> str:
        return repr(f"Transition(event={self.event}, target={self.target})")

    def callback(self) -> Callable:
        def event(machine, *args, **kwargs):
            machine._process_transitions(self.event, *args, **kwargs)
            log.info(f"processed transition event '{self.event}'")

        event.__name__ = self.event
        event.__doc__ = f"Show event: '{self.event}'."
        return event

    def evaluate(self, machine: 'StateChart') -> bool:
        return Guard(machine).evaluate(self.cond) if self.cond else True

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
        self.__transitions = transitions
        self.__state = self
        self.__states = {x.name: x for x in states}
        self.__on_entry = kwargs.get('on_entry')
        self.__on_exit = kwargs.get('on_exit')

        self.initial = kwargs.get('initial')

        for x in self.transitions:
            self.__register_transition_callback(x)
        # self._validate_state()

    def __repr__(self) -> str:
        return repr(f"State({self.name})")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, State):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name == other
        return False

    def __register_transition_callback(self, transition: 'Transition') -> None:
        # XXX: currently mapping to state instead of instance
        setattr(
            self,
            transition.event,
            transition.callback().__get__(self, self.__class__),
        )

    # def _validate_state(self) -> None:
    #     # TODO: empty statemachine should default to null event
    #     if self.kind == 'compund':
    #         if len(self.__states) < 2:
    #             raise InvalidConfig('There must be at least two states')
    #         if not self.initial:
    #             raise InvalidConfig('There must exist an initial state')
    #     log.info('evaluated state')

    @property
    def initial(self) -> Optional[str]:
        return self.__initial

    @initial.setter
    def initial(self, state: str) -> None:
        self.__initial = state
        if self.__state == self:
            self.__state = next(
                (v for k, v in self.states.items() if self.initial == k), self
            )

    @property
    def kind(self) -> str:
        if self.__kind:
            kind = self.__kind
        # elif self.states != [] and self.transitions != []:
        #     for x in self.transitions:
        #         if x == '':
        #             kind = 'transient'
        #             break
        #     else:
        #         kind = 'compound'
        elif self.states != []:
            kind = 'compound'
            # states:
            #   - parallel
            #   - and
            #   - or
        elif self.transitions != []:
            kind = 'atomic'
        else:
            kind = 'final'
        return kind

    @property
    def state(self) -> 'State':
        return self.__state

    @property
    def states(self) -> Dict[str, 'State']:
        return self.__states

    @property
    def transitions(self) -> List['Transition']:
        return self.__transitions

    def add_state(self, state: 'State') -> None:
        self.__states[state.name] = state

    def add_transition(self, transition: 'Transition') -> None:
        self.__transitions.append(transition)
        self.__register_transition_callback(transition)

    def get_transition(self, event: str) -> List['Transition']:
        return list(
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
    __slots__ = ['initial', '__states', '__dict__']
    initial: Union[Callable, str]

    def __init__(
        self,
        initial: Optional[Union[Callable, str]] = None,
        # states: List['State'] = [],
        **kwargs: Any,
    ) -> None:
        if 'logging_enabled' in kwargs and kwargs['logging_enabled']:
            log.addHandler(logging.StreamHandler())
            if 'logging_level' in kwargs:
                log.setLevel(kwargs['logging_level'].upper())
        log.info('initializing statemachine')

        self.__traverse_states = kwargs.get('traverse_states', False)

        if hasattr(self.__class__, '_root'):
            self.__superstate = self.__root = self.__class__._root
        else:
            raise InvalidConfig('There must be at least two states')

        # self.__states: Dict[str, 'State'] = {}
        # self.__states.update(self.__class__._states)
        # if states != []:
        #     self.__states.update({s.name: s for s in states})

        if initial:
            self.initial = initial
        elif self.superstate.initial:
            self.initial = self.superstate.initial
        else:
            raise InvalidConfig('There must exist an initial state')

        self._validate_machine()
        log.info('loaded states and transitions')

        # XXX: need to process callable from state with self
        self.initial = (
            self.initial(self) if callable(self.initial) else self.initial
        )
        self.__state = self.get_state(self.initial)
        self.__state._run_on_entry(self)
        log.info('statemachine initialization complete')

    def __getattr__(self, name: str) -> Any:
        if name == 'initial':
            raise InvalidConfig('There must exist an initial state')

        if name.startswith('is_'):
            try:
                return self.state.name == name[3:]
            except Exception:
                raise AttributeError

        # if self.__traverse_states:
        #     for key in list(self.__states.keys()):
        #         if key == name:
        #             return self.__items[name]

        try:
            for x in self.transitions + self.state.transitions:
                if x.event == name:
                    # XXX: need to improve this
                    return x.callback().__get__(self, self.__class__)
        # TODO: should iterate transitions and throw InvalidTransition on match
        except KeyError as err:
            print(err)

        raise AttributeError

    def _validate_machine(self) -> None:
        # TODO: empty statemachine should default to null event
        if len(self.__root.states) < 2:
            raise InvalidConfig('There must be at least two states')
        if not getattr(self, 'initial', None):
            raise InvalidConfig('There must exist an initial state')
        log.info('validated statemachine')

    @property
    def transitions(self) -> List['Transition']:
        return self.__superstate.transitions

    @property
    def superstate(self) -> 'State':
        return self.__superstate

    @property
    def states(self) -> List['State']:
        return list(self.superstate.states.values())

    @property
    def state(self) -> 'State':
        try:
            return self.__state
        except Exception:
            log.error('state is undefined')
            raise KeyError

    def get_state(self, query: str) -> 'State':
        paths = query.split('.')
        current = self.state if query.startswith('.') else self.__root
        for i, state in enumerate(paths):
            current = current.states[state]
            if i == (len(paths) - 1):
                log.info(f"found state '{current.name}'")
                return current
        raise InvalidState(f"state could not be found: {query}")

    def _change_state(self, state: str) -> None:
        superstate = state.split('.')[:-1]
        self.__supertstate = (
            self.get_state('.'.join(superstate))
            if superstate != []
            else self.__root
        )
        self.state._run_on_exit(self)
        self.__state = self.get_state(state)
        self.state._run_on_entry(self)
        log.info(f"changed state to {state}")

    def add_state(self, state: 'State', query: Optional[str] = None) -> None:
        parent = self.get_state(query) if query else self.__root
        parent.add_state(state)
        log.info(f"added state {state.name}")

    def add_transition(
        self, transition: 'Transition', state: Optional[str] = None
    ) -> None:
        target = self.get_state(state) if state else self.superstate
        target.add_transition(transition)
        log.info(f"added transition {transition.event}")

    def _process_transitions(
        self, event: str, *args: Any, **kwargs: Any
    ) -> None:
        _transitions = self.superstate.get_transition(event)
        _transitions += self.state.get_transition(event)
        if _transitions == []:
            raise InvalidTransition('no transitions match event')
        _transition = self.__evaluate_guards(_transitions)
        _transition.run(self, *args, **kwargs)

    def __evaluate_guards(
        self, transitions: List['Transition']
    ) -> 'Transition':
        allowed = []
        for _transition in transitions:
            if _transition.evaluate(self):
                allowed.append(_transition)
        if len(allowed) == 0:
            raise GuardNotSatisfied(
                'Guard is not satisfied for this transition'
            )
        elif len(allowed) > 1:
            raise ForkedTransition(
                'More than one transition was allowed for this event'
            )
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
