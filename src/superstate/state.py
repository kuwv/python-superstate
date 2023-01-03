"""Provide states for statechart."""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Tuple

from superstate.exec import Action
from superstate.exception import InvalidConfig, InvalidTransition

# from superstate.models import NameDescriptor

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
#     _initial: Optional['InitialType']
#     _kind: Optional[str]
#     _states: List['State']
#     _transitions: List['State']
#     _on_entry: Optional['EventActions']
#     _on_exit: Optional['EventActions']
#
#     def __new__(
#         cls,
#         name: str,
#         bases: Tuple[type, ...],
#         attrs: Dict[str, Any],
#     ) -> 'MetaState':
#         _initial = attrs.pop('__initial__', None)
#         _kind = attrs.pop('__kind__', None)
#         _states = attrs.pop('__states__', None)
#         _transitions = attrs.pop('__transitions__', None)
#         _on_entry = attrs.pop('__on_entry__', None)
#         _on_exit = attrs.pop('__on_exit__', None)
#
#         obj = type.__new__(cls, name, bases, attrs)
#         obj._initial = _initial
#         obj._kind = _kind
#         obj._states = _states
#         obj._transitions = _transitions
#         obj._on_entry = _on_entry
#         obj._on_exit = _on_exit
#         print(vars(obj))
#         return obj


class State:
    """Provide pseudostate base for various pseudostate types."""

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
    superstate: Optional['CompositeState']

    # pylint: disable-next=unused-argument
    def __new__(cls, *args: Any, **kwargs: Any) -> 'State':
        """Return state type."""
        kind = kwargs.get('kind')
        states = kwargs.get('states')
        transitions = kwargs.get('transitions')
        if states and transitions:
            # for transition in self.transitions:
            #     if transition == '':
            #         kind = 'transient'
            #         break
            # else:
            kind = 'compound'
        elif states:
            if 'initial' not in kwargs:
                kind = 'parallel'
            kind = 'compound'
        # elif _transitions:
        #     kind = 'conditional'
        else:
            kind = 'atomic'

        for subclass in cls.lookup_subclasses(cls):
            if subclass.__name__.lower().startswith(kind):
                return super().__new__(subclass)
        return super().__new__(cls)

    def __init__(
        self,  # pylint: disable=unused-argument
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.__name = name
        self.__kind = kwargs.get('kind', 'atomic')

    @classmethod
    def lookup_subclasses(cls, obj: Type['State']):
        """Get all subsclasses."""
        return set(obj.__subclasses__()).union(
            [s for c in obj.__subclasses__() for s in cls.lookup_subclasses(c)]
        )

    @property
    def name(self) -> 'str':
        """Get name of state."""
        return self.__name

    @property
    def kind(self) -> 'str':
        """Get state type."""
        return self.__kind

    def __repr__(self) -> str:
        return repr(f"{self.__class__.__name__}({self.name})")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.__name == other.name
        if isinstance(other, str):
            return self.__name == other
        return False

    def run_on_entry(self, machine: 'StateChart') -> None:
        """Run on-entry tasks."""
        raise NotImplementedError

    def run_on_exit(self, machine: 'StateChart') -> None:
        """Run on-exit tasks."""
        raise NotImplementedError


class PseudoState(State):
    """Provide state for statechart."""

    def run_on_entry(self, machine: 'StateChart') -> None:
        """Run on-entry tasks."""
        raise InvalidTransition('cannot transition to pseudostate')

    def run_on_exit(self, machine: 'StateChart') -> None:
        """Run on-exit tasks."""
        raise InvalidTransition('cannot transition from pseudostate')


class ConditionState(PseudoState):
    """A pseudostate that only transits to other states."""

    __transitions: List['Transition']

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        """Initialize atomic state."""
        self.__transitions = kwargs.pop('transitions', [])
        super().__init__(name, *args, **kwargs)

    @property
    def transitions(self) -> Tuple['Transition', ...]:
        """Return transitions of this state."""
        return tuple(self.__transitions)

    def add_transition(self, transition: 'Transition') -> None:
        """Add transition to this state."""
        self.__transitions.append(transition)


class HistoryState(PseudoState):
    """A pseudostate that remembers transition history of compound states."""

    __history: str

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        self.__history = kwargs.get('history', 'shallow')
        super().__init__(name, *args, **kwargs)

    @property
    def history(self) -> str:
        """Return previous substate."""
        return self.__history


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


class AtomicState(State):
    """Provide an atomic state for a statechart."""

    __transitions: List['Transition']
    __on_entry: Optional['EventActions']
    __on_exit: Optional['EventActions']

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        """Initialize atomic state."""
        self.__transitions = kwargs.pop('transitions', [])
        for transition in self.transitions:
            self.__register_transition_callback(transition)
        self.__on_entry = kwargs.pop('on_entry', None)
        self.__on_exit = kwargs.pop('on_exit', None)
        super().__init__(name, *args, **kwargs)

    def __register_transition_callback(self, transition: 'Transition') -> None:
        # XXX: currently mapping to class instead of instance
        setattr(
            self,
            transition.event if transition.event != '' else '_auto_',
            transition.callback().__get__(self, self.__class__),
        )

    @property
    def transitions(self) -> Tuple['Transition', ...]:
        """Return transitions of this state."""
        return tuple(self.__transitions)

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

    def __process_transient_state(self, machine: 'StateChart') -> None:
        for transition in self.transitions:
            if transition.event == '':
                # pylint: disable-next=protected-access
                machine._auto_()
                break

    def run_on_entry(self, machine: 'StateChart') -> None:
        self.__process_transient_state(machine)
        if self.__on_entry is not None:
            Action(machine).run(self.__on_entry)
            log.info(
                "executed 'on_entry' state change action for %s", self.name
            )

    def run_on_exit(self, machine: 'StateChart') -> None:
        if self.__on_exit is not None:
            Action(machine).run(self.__on_exit)
            log.info(
                "executed 'on_exit' state change action for %s", self.name
            )


class CompositeState(AtomicState):
    """Provide composite abstract to define nested state types."""

    def __getattr__(self, name: str) -> Any:
        if name.startswith('__'):
            raise AttributeError

        for key in self.substates:
            if key == name:
                return self.substates[name]
        raise AttributeError

    @property
    def substates(self) -> Dict[str, 'State']:
        """Return substates."""
        raise NotImplementedError

    def add_state(self, state: 'State') -> None:
        """Add substate to this state."""
        raise NotImplementedError

    def is_current_state(self, name: str) -> bool:
        """Check current active state by name."""
        raise NotImplementedError

    def get_state(self, name: str) -> Optional['State']:
        """Get state by name."""
        return self.substates.get(name)


class ParallelState(CompositeState):
    """Provide parallel state capability for statechart."""

    __substates: Dict[str, 'State']

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        """Initialize compound state."""
        for x in kwargs.pop('states', []):
            x.superstate = self
            self.__substates[x.name] = x
        super().__init__(name, *args, **kwargs)

    @property
    def substates(self) -> Dict[str, 'State']:
        """Return substates."""
        return self.__substates

    def add_state(self, state: 'State') -> None:
        """Add substate to this state."""
        state.superstate = self
        self.__substates[state.name] = state

    def is_current_state(self, name: str) -> bool:
        for state in self.__substates:
            if state == name[3:]:
                return True
        return False

    def run_on_entry(self, machine: 'StateChart') -> None:
        super().run_on_entry(machine)
        for substate in reversed(self.__substates.values()):
            substate.run_on_entry(machine)

    def run_on_exit(self, machine: 'StateChart') -> None:
        for substate in reversed(self.__substates.values()):
            substate.run_on_exit(machine)
        super().run_on_exit(machine)

    # def validate(self) -> None:
    #     # TODO: empty statemachine should default to null event
    #     if self.kind == 'compund':
    #         if len(self.__substates) < 2:
    #             raise InvalidConfig('There must be at least two states')
    #         if not self.initial:
    #             raise InvalidConfig('There must exist an initial state')
    #     if self.initial and self.kind == 'parallel':
    #         raise InvalidConfig(
    #             'parallel state should not have an initial state'
    #         )
    #     if self.kind == 'final' and self.__on_exit:
    #         log.warning('final state will never run "on_exit" action')
    #     log.info('evaluated state')


class CompoundState(CompositeState):
    """Provide nested state capabilitiy."""

    initial: 'InitialType'
    __substate: 'State'

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        self.__substate = self
        self.__substates = {}
        for x in kwargs.pop('states', []):
            x.superstate = self
            self.__substates[x.name] = x
        self.initial = kwargs.pop('initial')
        super().__init__(name, *args, **kwargs)

    @property
    def substate(self) -> 'State':
        """Current substate of this state."""
        return self.__substate

    def change_state(self, name: str, machine: 'StateChart') -> None:
        """Current substate of this state."""
        log.info("running on-exit tasks for state '%s'", name)
        self.__substate.run_on_exit(machine)
        self.__substate = self.__substates[name]
        log.info('state is now: %s', name)
        log.info("running on-entry tasks for state: '%s'", name)
        self.__substate.run_on_entry(machine)

    @property
    def substates(self) -> Dict[str, 'State']:
        """Return substates."""
        return self.__substates

    def is_current_state(self, name: str) -> bool:
        return self.__substate.name == name[3:]

    def add_state(self, state: 'State') -> None:
        """Add substate to this state."""
        state.superstate = self
        self.__substates[state.name] = state

    def run_on_entry(self, machine: 'StateChart') -> None:
        super().run_on_entry(machine)
        # if next(
        #     (x for x in self.substates if isinstance(x, HistoryState)), False
        # ):
        #     ...
        if self.initial:
            self.__substate = (
                self.get_state(
                    self.initial(self)
                    if callable(self.initial)
                    else self.initial
                )
                or self
            )
        else:
            raise InvalidConfig('an initial state must exist for statechart')

    # def run_on_exit(self, machine: 'StateChart') -> None:
    #     super().run_on_exit(machine)

    def validate(self) -> None:
        """Validate state to ensure conformance with type requirements."""
        if len(self.__substates) < 2:
            raise InvalidConfig('There must be at least two states')
        if not self.initial:
            raise InvalidConfig('There must exist an initial state')
