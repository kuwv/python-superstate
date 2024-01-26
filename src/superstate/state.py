"""Provide states for statechart."""

import logging
from itertools import chain  # , zip_longest
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    List,
    Optional,
    Sequence,
    Set,
    Type,
    Tuple,
)

from superstate.exception import InvalidConfig, InvalidTransition
from superstate.utils import tuplize

# from superstate.model import NameDescriptor

if TYPE_CHECKING:
    from superstate.machine import StateChart
    from superstate.model import Data, DataModel
    from superstate.transition import Transition
    from superstate.types import EventActions, InitialType

log = logging.getLogger(__name__)


# class MetaState(type):
#     """Instantiate state types from class metadata."""
#
#     _initial: Optional['InitialType']
#     _type: Optional[str]
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
#         _kind = attrs.pop('__type__', None)
#         _states = attrs.pop('__states__', None)
#         _transitions = attrs.pop('__transitions__', None)
#         _on_entry = attrs.pop('__on_entry__', None)
#         _on_exit = attrs.pop('__on_exit__', None)
#
#         obj = type.__new__(cls, name, bases, attrs)
#         obj._initial = _initial
#         obj._kind = _type
#         obj._states = _states
#         obj._transitions = _transitions
#         obj._on_entry = _on_entry
#         obj._on_exit = _on_exit
#         return obj


class State:
    """Provide pseudostate base for various pseudostate types."""

    # __slots__ = [
    #     '_name',
    #     '__initial',
    #     '__state',
    #     '__states',
    #     '__transitions',
    #     '__on_entry',
    #     '__on_exit',
    #     '__type',
    # ]

    __datamodel: Optional['DataModel']
    # name = cast(str, NameDescriptor('_name'))
    current_state: 'State'

    # pylint: disable-next=unused-argument
    def __new__(cls, *args: Any, **kwargs: Any) -> 'State':
        """Return state type."""
        kind = kwargs.get('type')
        states = kwargs.get('states')
        # transitions = kwargs.get('transitions')
        # if states and transitions:
        #     # for transition in self.transitions:
        #     #     if transition == '':
        #     #         kind = 'transient'
        #     #         break
        #     # else:
        #     kind = 'compound'
        if states:
            if 'initial' in kwargs:
                kind = 'compound'
            else:
                kind = 'parallel'
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
        self.__parent: Optional['CompositeState'] = None
        self.__name = name
        self.__type = kwargs.get('type', 'atomic')
        self.__datamodel = kwargs.pop('datamodel', None)
        # self.__ctx: Optional['StateChart'] = None
        # self.validate()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return False

    def __repr__(self) -> str:
        return repr(f"{self.__class__.__name__}({self.name})")

    def __reversed__(self) -> Generator['State', None, None]:
        target: Optional['State'] = self
        while target:
            yield target
            target = target.parent

    @classmethod
    def lookup_subclasses(cls, obj: Type['State']) -> Set[Type['State']]:
        """Get all subsclasses."""
        return set(obj.__subclasses__()).union(
            [s for c in obj.__subclasses__() for s in cls.lookup_subclasses(c)]
        )

    @property
    def name(self) -> 'str':
        """Get name of state."""
        return self.__name

    @property
    def datamodel(self) -> Optional['DataModel']:
        """Get datamodel data items."""
        return self.__datamodel

    @property
    def data(self) -> Sequence['Data']:
        """Get datamodel data items."""
        return self.__datamodel.data if self.__datamodel else ()

    @property
    def path(self) -> str:
        """Get the statepath of this state."""
        return '.'.join(
            reversed([x.name for x in reversed(self)])  # type: ignore
        )

    # @property
    # def relpath(self) -> str:
    #     if self.path == target:
    #         relpath = '.'
    #     else:
    #         path = ['']
    #         source_path = self.path.split('.')
    #         target_path = target.split('.')
    #         for i, x in enumerate(
    #             zip_longest(source_path, target_path, fillvalue='')
    #         ):
    #             if x[0] != x[1]:
    #                 if i == 0:
    #                     raise Exception('no relative path exists')
    #                 if x[0] != '':
    #                     path.extend(['' for x in source_path[i:]])
    #                 if x[1] != '':
    #                     path.extend(target_path[i:])
    #                 break
    #         relpath = '.'.join(path)
    #     return relpath

    @property
    def type(self) -> 'str':
        """Get state type."""
        return self.__type

    @property
    def parent(self) -> Optional['CompositeState']:
        """Get parent state."""
        return self.__parent

    @parent.setter
    def parent(self, state: 'CompositeState') -> None:
        if self.__parent is None:
            self.__parent = state
        else:
            raise Exception('cannot change parent for state')

    # def ctx(self) -> Optional['StateChart']:
    #     """Get current ctx of the statechart."""
    #     return self.__ctx

    # @ctx.setter
    # def ctx(self, ctx: 'StateChart') -> None:
    #     """Set the current ctx of the statechart."""
    #     if not self.ctx:
    #         self.__ctx = ctx

    def run_on_entry(self, ctx: 'StateChart') -> Optional[Any]:
        """Run on-entry tasks."""
        # raise NotImplementedError

    def run_on_exit(self, ctx: 'StateChart') -> Optional[Any]:
        """Run on-exit tasks."""
        # raise NotImplementedError


class PseudoState(State):
    """Provide state for statechart."""

    def run_on_entry(self, ctx: 'StateChart') -> Optional[Any]:
        """Run on-entry tasks."""
        raise InvalidTransition('cannot transition to pseudostate')

    def run_on_exit(self, ctx: 'StateChart') -> Optional[Any]:
        """Run on-exit tasks."""
        raise InvalidTransition('cannot transition from pseudostate')


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


class FinalState(State):
    """Provide final state for a statechart."""

    __on_entry: Optional['EventActions']

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        # if 'donedata' in kwargs:
        #     self.__data = kwargs.pop('donedata')
        super().__init__(name, *args, **kwargs)
        self.__on_entry = kwargs.get('on_entry')

    def run_on_entry(self, ctx: 'StateChart') -> Optional[Any]:
        # NOTE: SCXML Processor MUST generate the event done.state.id after
        # completion of the <onentry> elements
        if self.__on_entry:
            ActionModel = (
                ctx.datamodel.script
                if ctx.datamodel and ctx.datamodel.script
                else None
            )
            if ActionModel:
                result = tuple(
                    ActionModel(ctx).run(x)  # , *args, **kwargs)
                    for x in tuplize(self.__on_entry)
                )
                log.info(
                    "executed 'on_entry' state change action for %s", self.name
                )
                return result
        return None

    def run_on_exit(self, ctx: 'StateChart') -> Optional[Any]:
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

    def _process_transient_state(self, ctx: 'StateChart') -> None:
        for transition in self.transitions:
            if transition.event == '':
                ctx._auto_()  # pylint: disable=protected-access
                break

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

    def run_on_entry(self, ctx: 'StateChart') -> Optional[Any]:
        self._process_transient_state(ctx)
        if self.__on_entry:
            ActionModel = (
                ctx.datamodel.script
                if ctx.datamodel and ctx.datamodel.script
                else None
            )
            if ActionModel:
                result = tuple(
                    ActionModel(ctx).run(x)  # , *args, **kwargs)
                    # ctx.datamodel.script(ctx).run(x)  # , *args, **kwargs)
                    for x in tuplize(self.__on_entry)
                )
                log.info(
                    "executed 'on_entry' state change action for %s", self.name
                )
                return result
        return None

    def run_on_exit(self, ctx: 'StateChart') -> Optional[Any]:
        if self.__on_exit:
            ActionModel = (
                ctx.datamodel.script
                if ctx.datamodel and ctx.datamodel.script
                else None
            )
            if ActionModel:
                result = tuple(
                    ActionModel(ctx).run(x)  # , *args, **kwargs)
                    for x in tuplize(self.__on_exit)
                )
                log.info(
                    "executed 'on_exit' state change action for %s", self.name
                )
                return result
        return None


class CompositeState(AtomicState):
    """Provide composite abstract to define nested state types."""

    __stack: List['State']

    def __getattr__(self, name: str) -> Any:
        if name.startswith('__'):
            raise AttributeError
        for key in self.states:
            if key == name:
                return self.states[name]
        raise AttributeError

    def __iter__(self) -> 'CompositeState':
        self.__stack = [self]
        return self

    def __next__(self) -> 'State':
        # simple breadth-first iteration
        if self.__stack:
            x = self.__stack.pop()
            if isinstance(x, CompositeState):
                self.__stack = list(chain(x.states.values(), self.__stack))
            return x
        raise StopIteration

    @property
    def states(self) -> Dict[str, 'State']:
        """Return states."""
        raise NotImplementedError

    def add_state(self, state: 'State') -> None:
        """Add substate to this state."""
        raise NotImplementedError

    def is_active(self, name: str) -> bool:
        """Check current active state by name."""
        raise NotImplementedError

    def get_state(self, name: str) -> Optional['State']:
        """Get state by name."""
        return self.states.get(name)


class CompoundState(CompositeState):
    """Provide nested state capabilitiy."""

    # __state: 'State'
    initial: 'InitialType'
    final: 'FinalState'

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        # self.__state = self
        self.__states = {}
        for state in kwargs.pop('states', []):
            state.parent = self
            self.__states[state.name] = state
        self.initial = kwargs.pop('initial')
        super().__init__(name, *args, **kwargs)

    # @property
    # def substate(self) -> 'State':
    #     """Current substate of this state."""
    #     return self.__state

    # @substate.setter
    # def substate(self, state: 'State') -> None:
    #     """Set current substate of this state."""
    #     try:
    #         self.__state = self.states[state.name]
    #     except KeyError as err:
    #         raise InvalidState(
    #             f"substate could not be found: {state.name}"
    #         ) from err

    @property
    def states(self) -> Dict[str, 'State']:
        """Return states."""
        return self.__states

    def is_active(self, name: str) -> bool:
        """Check if a state is active or not."""
        return self.substate.name == name

    def add_state(self, state: 'State') -> None:
        """Add substate to this state."""
        state.parent = self
        self.__states[state.name] = state

    def run_on_entry(self, ctx: 'StateChart') -> Optional[Tuple[Any, ...]]:
        # if next(
        #     (x for x in self.states if isinstance(x, HistoryState)), False
        # ):
        #     ...
        # XXX: initial can be None
        if not self.initial:
            raise InvalidConfig('an initial state must exist for statechart')
        if self.initial:
            initial = (
                self.initial(ctx) if callable(self.initial) else self.initial
            )
            if initial:
                ctx.change_state(initial)
        results: List[Any] = []
        results += filter(None, [super().run_on_entry(ctx)])
        if hasattr(ctx.state, 'initial') and ctx.state.initial:
            ctx.change_state(ctx.state.initial)
        return tuple(results) if results else None

    # def validate(self) -> None:
    #     """Validate state to ensure conformance with type requirements.

    #     The configuration contains exactly one child of the <scxml> element.
    #     The configuration contains one or more atomic states.
    #     When the configuration contains an atomic state, it contains all of
    #         its <state> and <parallel> ancestors.
    #     When the configuration contains a non-atomic <state>, it contains one
    #         and only one of the state's states.
    #     If the configuration contains a <parallel> state, it contains all of
    #         its states.
    #     """

    #     if len(self.__states) < 1:
    #         raise InvalidConfig('There must be one or more states')
    #     if not self.initial:
    #         raise InvalidConfig('There must exist an initial state')


class ParallelState(CompositeState):
    """Provide parallel state capability for statechart."""

    __states: Dict[str, 'State']

    def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
        """Initialize compound state."""
        self.__states = {}
        for x in kwargs.pop('states', []):
            x.parent = self
            self.__states[x.name] = x
        super().__init__(name, *args, **kwargs)

    @property
    def states(self) -> Dict[str, 'State']:
        """Return states."""
        return self.__states

    def add_state(self, state: 'State') -> None:
        """Add substate to this state."""
        state.parent = self
        self.__states[state.name] = state

    def is_active(self, name: str) -> bool:
        for state in self.states:
            if state == name:
                return True
        return False

    def run_on_entry(
        self, ctx: 'StateChart'
    ) -> Optional[Any]:
        results = []
        results.append(super().run_on_entry(ctx))
        for state in reversed(self.states.values()):
            results.append(state.run_on_entry(ctx))
        return results

    def run_on_exit(self, ctx: 'StateChart') -> Optional[Any]:
        results = []
        for state in reversed(self.states.values()):
            results.append(state.run_on_exit(ctx))
        results.append(super().run_on_exit(ctx))
        return results

    # def validate(self) -> None:
    #     # TODO: empty statemachine should default to null event
    #     if self.type == 'compund':
    #         if len(self.__states) < 2:
    #             raise InvalidConfig('There must be at least two states')
    #         if not self.initial:
    #             raise InvalidConfig('There must exist an initial state')
    #     if self.initial and self.type == 'parallel':
    #         raise InvalidConfig(
    #             'parallel state should not have an initial state'
    #         )
    #     if self.type == 'final' and self.__on_exit:
    #         log.warning('final state will never run "on_exit" action')
    #     log.info('evaluated state')
