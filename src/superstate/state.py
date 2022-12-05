"""Provide states for statechart."""

import logging

from abc import ABC, abstractmethod

# from types import new_class
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from superstate.common import Action
from superstate.exception import InvalidConfig, InvalidTransition
from superstate.transition import transitions

# from superstate.types import NameDescriptor

if TYPE_CHECKING:
    from superstate.machine import StateChart
    from superstate.transition import Transition
    from superstate.types import (
        EventActions,
        InitialType,
    )

log = logging.getLogger(__name__)


# class MetaState(type):
#     """Instantiate state types from class metadata."""
#
#     # initial: Optional[Union[Callable, str]]
#     # _states: List['State']
#     # _transitions: List['State']
#     # on_entry:
#     # on_exit:
#
#     # @classmethod
#     # def __prepare__(
#     #     mcs, name: str, bases: Tuple[type, ...], **kwargs: Any
#     # ) -> Dict[str, Any]:
#     #     ...
#
#     def __new__(
#         cls,
#         name: str,
#         bases: Tuple[type, ...],
#         attrs: Dict[str, Any],
#     ) -> 'MetaState':
#         # initial = attrs.pop('initial', None)
#         # kind = attrs.pop('kind')
#         # _states = attrs.pop('__states__', None)
#         # _transitions = attrs.pop('__transitions__', None)
#         # on_entry = attrs.pop('on_entry', None)
#         # on_exit = attrs.pop('on_exit', None)
#
#         obj = super().__new__(cls, name, bases, attrs)
#         # obj.initial = states
#         # obj._states = _states
#         # obj._transitions = _transitions
#         # obj.on_entry = on_entry
#         # obj.on_exit = on_exit
#
#         return obj


class PseudoState(ABC):
    """Provide state for statechart."""

    # __slots__ = [
    #     '_name',
    #     '__initial',
    #     '__substate',
    #     '__substates',
    #     '__transitions',
    #     '__on_entry',
    #     '__on_exit',
    #     '__kind',
    # ]
    # name = cast(str, NameDescriptor('_name'))

    def __new__(cls, *args: Any, **kwargs: Any) -> 'PseudoState':
        """Return state type."""
        kind = kwargs.get('kind')
        if not kind:
            _states = kwargs.get('states')
            _transitions = kwargs.get('transitions')
        if _states and _transitions:
            # for transition in self.transitions:
            #     if transition == '':
            #         kind = 'transient'
            #         break
            # else:
            kind = 'compound'
        elif _states:
            if 'initial' not in kwargs:
                kind = 'parallel'
            kind = 'compound'
        # elif _transitions:
        #     kind = 'conditional'
        else:
            kind = 'atomic'

        print(cls.__name__)
        print(kind, [x.__name__ for x in cls.__subclasses__()])
        for i in cls.__subclasses__():
            if i.__name__.lower().startswith(kind):
                return super().__new__(i, *args, **kwargs)
        raise InvalidConfig('state type is not supported')

    def __init__(
        self,  # pylint: disable=unused-argument
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.__name = name
        self.__kind = kwargs.get('kind', 'atomic')

    @property
    def name(self) -> 'str':
        """Get name of state."""
        return self.__name

    @property
    def kind(self) -> 'str':
        """Get state type."""
        return self.__kind

    def __repr__(self) -> str:
        return repr(f"State({self.name})")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PseudoState):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return False


class HistoryState(PseudoState):
    """Provide history transition for compound states."""

    __history: str

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        self.__history = kwargs.get('history', 'shallow')
        super().__init__(name, *args, **kwargs)

    @property
    def kind(self) -> str:
        """Return state type."""
        return 'history'

    @property
    def history(self) -> str:
        """Return previous substate."""
        return self.__history


class State(PseudoState):
    """Provide state for statechart."""

    @abstractmethod
    def run_on_entry(self, machine: 'StateChart') -> None:
        """Run on-entry tasks."""

    @abstractmethod
    def run_on_exit(self, machine: 'StateChart') -> None:
        """Run on-exit tasks."""


class FinalState(State):
    """Provide final state for a statechart."""

    __on_entry: Optional['EventActions']

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(name, *args, **kwargs)
        self.__on_entry = kwargs.get('on_entry')

    def run_on_entry(self, machine: 'StateChart') -> None:
        if self.__on_entry is not None:
            Action(machine).run(self.__on_entry)
            log.info(
                "executed 'on_entry' state change action for %s", self.name
            )

    def run_on_exit(self, machine: 'StateChart') -> None:
        raise InvalidTransition('final state cannot transition once entered')


class AtomicState(FinalState):
    """Provide an atomic state for a statechart."""

    __on_exit: Optional['EventActions']

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(name, *args, **kwargs)
        self.__on_exit = kwargs.get('on_exit')

    def run_on_exit(self, machine: 'StateChart') -> None:
        if self.__on_exit is not None:
            Action(machine).run(self.__on_exit)
            log.info(
                "executed 'on_exit' state change action for %s", self.name
            )


class CompositeState(AtomicState):
    """Provide composite abstract to define nested state types."""

    @property
    @abstractmethod
    def substates(self) -> Dict[str, 'State']:
        """Return substates."""

    @property
    @abstractmethod
    def transitions(self) -> Tuple['Transition', ...]:
        """Return transitions of this state."""

    @abstractmethod
    def get_transition(self, event: str) -> Tuple['Transition', ...]:
        """Get each transition maching event."""

    @abstractmethod
    def add_state(self, state: 'State') -> None:
        """Add substate to this state."""

    @abstractmethod
    def add_transition(self, transition: 'Transition') -> None:
        """Add transition to this state."""


class ParallelState(AtomicState):
    """Provide parallel state capability for statechart."""

    __substates: Dict[str, 'State']
    __transitions: List['Transition']

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        """Initialize compound state."""
        self.__substates = {x.name: x for x in kwargs.get('states', [])}
        self.__transitions = kwargs.get('transitions', [])
        for transition in self.transitions:
            self.__register_transition_callback(transition)
        super().__init__(name, *args, **kwargs)

    def __register_transition_callback(self, transition: 'Transition') -> None:
        # XXX: currently mapping to class instead of instance
        setattr(
            self,
            transition.event if transition.event != '' else '_auto_',
            transition.callback().__get__(self, self.__class__),
        )

    @property
    def substates(self) -> Dict[str, 'State']:
        """Return substates."""
        return self.__substates

    @property
    def transitions(self) -> Tuple['Transition', ...]:
        """Return transitions of this state."""
        return tuple(self.__transitions)

    def get_transition(self, event: str) -> Tuple['Transition', ...]:
        """Get each transition maching event."""
        return tuple(
            filter(
                lambda transition: transition.event == event, self.transitions
            )
        )

    def add_state(self, state: 'State') -> None:
        """Add substate to this state."""
        self.__substates[state.name] = state

    def add_transition(self, transition: 'Transition') -> None:
        """Add transition to this state."""
        self.__transitions.append(transition)
        self.__register_transition_callback(transition)


class CompoundState(ParallelState):
    """Provide nested state capabilitiy."""

    __initial: Optional['InitialType']
    __substate: 'CompoundState'

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        self.__substate = self
        super().__init__(name, *args, **kwargs)
        self.__initial = kwargs.get('initial', None)

    @property
    def initial(self) -> Optional['InitialType']:
        """Return initial substate if defined."""
        return self.__initial

    @property
    def substate(self) -> 'CompoundState':
        """Current substate of this state."""
        return self.__substate

    def validate(self) -> None:
        """Validate state to ensure conformance with type requirements."""
        if len(self.__substates) < 2:
            raise InvalidConfig('There must be at least two states')
        if not self.initial:
            raise InvalidConfig('There must exist an initial state')


def state(config: Union['State', dict, str]) -> 'PseudoState':
    """Create state from configuration."""
    if isinstance(config, State):
        return config
    if isinstance(config, str):
        return AtomicState(config)
    if isinstance(config, dict):
        # kind = config.get('kind', 'atomic')
        # factory = State
        # if kind in ('compound', 'parallel') or 'states' in config:
        #     factory = CompoundState if 'initial' in config else ParallelState
        # elif kind == 'final':
        #     factory = FinalState
        # # elif kind == 'history' or 'history' in config:
        # #     factory = HistoryState
        # elif kind == 'atomic':
        #     factory = AtomicState

        # cls = new_class(
        #     'State',
        #     bases=(factory,),
        #     kwds={},  # 'metaclass': MetaState},
        #     exec_body=None,
        # )

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


def states(*args: Any) -> List['PseudoState']:
    """Create states from configuration."""
    return list(map(state, args))
