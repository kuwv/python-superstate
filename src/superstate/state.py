"""Provide states for statechart."""

from __future__ import annotations

import logging
from itertools import chain  # , zip_longest
from typing import TYPE_CHECKING, Any, Generator, Optional, Union, cast

from superstate.exception import (
    InvalidConfig,
    InvalidTransition,
    SuperstateException,
)
from superstate.model.base import Action
from superstate.model.data import DataModel
from superstate.transition import Transition
from superstate.types import Identifier, Selection
from superstate.utils import lookup_subclasses, tuplize

if TYPE_CHECKING:
    from superstate.machine import StateChart
    from superstate.types import ActionTypes, Initial

log = logging.getLogger(__name__)


# class MetaState(type):
#     """Instantiate state types from class metadata."""
#
#     initial: Optional[Initial]
#     kind: Optional[str]
#     states: list[State]
#     transitions: list[State]
#     on_entry: Optional[ActionTypes]
#     on_exit: Optional[ActionTypes]
#
#     def __new__(
#         cls,
#         name: str,
#         bases: tuple[type, ...],
#         attrs: dict[str, Any],
#     ) -> 'MetaState':
#         initial = attrs.pop('initial', None)
#         kind = attrs.pop('type', None)
#         states = attrs.pop('states', None)
#         transitions = attrs.pop('transitions', None)
#         on_entry = attrs.pop('on_entry', None)
#         on_exit = attrs.pop('on_exit', None)
#
#         obj = type.__new__(cls, name, bases, attrs)
#         obj.initial = initial
#         obj.kind = kind
#         obj.states = states
#         obj.transitions = transitions
#         obj.on_entry = on_entry
#         obj.on_exit = on_exit
#         return obj


class TransitionMixin:
    """Provide an atomic state for a statechart."""

    __transitions: list[Transition]

    @property
    def transitions(self) -> tuple[Transition, ...]:
        """Return transitions of this state."""
        return tuple(self.__transitions)

    @transitions.setter
    def transitions(self, transitions: list[Transition]) -> None:
        """Initialize atomic state."""
        self.__transitions = transitions

    def add_transition(self, transition: Transition) -> None:
        """Add transition to this state."""
        self.__transitions.append(transition)

    def get_transition(self, event: str) -> tuple[Transition, ...]:
        """Get each transition maching event."""
        return tuple(
            filter(
                lambda transition: transition.event == event, self.transitions
            )
        )


class ContentMixin:
    """Provide an atomic state for a statechart."""

    name: str
    __on_entry: Optional[ActionTypes]
    __on_exit: Optional[ActionTypes]

    @property
    def on_entry(self) -> Optional[ActionTypes]:
        """Return on-entry content of this state."""
        return self.__on_entry

    @on_entry.setter
    def on_entry(self, content: ActionTypes) -> None:
        """Set on-entry content of this state."""
        self.__on_entry = content

    @property
    def on_exit(self) -> Optional[ActionTypes]:
        """Return on-exit content of this state."""
        return self.__on_entry

    @on_exit.setter
    def on_exit(self, content: ActionTypes) -> None:
        """Set on-exit content of this state."""
        self.__on_exit = content

    def run_on_entry(self, ctx: StateChart) -> Optional[Any]:
        """Run on-entry tasks."""
        if self.__on_entry:
            results = []
            executor = ctx.datamodel.provider(ctx)
            for expression in self.__on_entry:
                results.append(executor.handle(expression))  # *args, **kwargs))
            log.info(
                "executed 'on_entry' state change action for %s", self.name
            )
            return results
        return None

    def run_on_exit(self, ctx: StateChart) -> Optional[Any]:
        """Run on-exit tasks."""
        if self.__on_exit:
            results = []
            executor = ctx.datamodel.provider(ctx)
            for expression in self.__on_exit:
                results.append(executor.handle(expression))  # *args, **kwargs))
            log.info("executed 'on_exit' state change action for %s", self.name)
            return results
        return None


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

    __stack: list[State]
    datamodel: DataModel
    name: str = cast(str, Identifier())
    # history: Optional['HistoryState']
    # final: Optional[FinalState]
    states: dict[str, State]
    # transitions: tuple[Transition, ...]
    # onentry: tuple[ActionTypes, ...]
    # onexit: tuple[ActionTypes, ...]

    # pylint: disable-next=unused-argument
    def __new__(cls, *args: Any, **kwargs: Any) -> State:
        """Return state type."""
        kind = kwargs.get('type')
        if kind is None:
            if kwargs.get('states'):
                if 'initial' in kwargs:
                    kind = 'compound'
                else:
                    kind = 'parallel'
            # elif transitions:
            #     kind = 'evaluator'
            else:
                kind = 'atomic'
        for subclass in lookup_subclasses(cls):
            if subclass.__name__.lower().startswith(kind):
                return super().__new__(subclass)
        return super().__new__(cls)

    def __init__(
        self,  # pylint: disable=unused-argument
        name: str,
        # settings: Optional[dict[str, Any]] = None,
        # /,
        **kwargs: Any,
    ) -> None:
        # TODO: should place the initial state here instead of onentry
        self.__type = kwargs.get('type', 'atomic')
        self.__parent: Optional[SubstateMixin] = None
        self.name = name
        self.datamodel = kwargs.pop('datamodel', DataModel([]))
        self.datamodel.parent = self
        if self.datamodel.binding == 'early':
            self.datamodel.populate()
        self.validate()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return False

    def __repr__(self) -> str:
        return repr(f"{self.__class__.__name__}({self.name})")

    def __iter__(self) -> State:
        self.__stack = [self]
        return self

    def __next__(self) -> State:
        # simple breadth-first iteration
        if self.__stack:
            x = self.__stack.pop()
            if isinstance(x, SubstateMixin):
                self.__stack = list(chain(x.states.values(), self.__stack))
            return x
        raise StopIteration

    def __reversed__(self) -> Generator[State, None, None]:
        target: Optional[State] = self
        while target:
            yield target
            target = target.parent

    @classmethod
    def create(
        cls, settings: Union[State, dict, str]
    ) -> Union[SubstateMixin, State]:
        """Create state from configuration."""
        obj = None
        if isinstance(settings, State):
            obj = settings
        elif isinstance(settings, dict):
            obj = settings.pop('factory', State)(
                name=settings.get('name', 'root'),
                initial=settings.get('initial'),
                # TODO: standardize initial state
                # initial=(
                #     InitialState.create(settings['initial'])
                #     if 'initial' in settings
                #     else None
                # ),
                type=settings.get('type'),
                datamodel=DataModel.create(
                    settings.get('datamodel', {'data': {}})
                ),
                states=(
                    list(map(State.create, settings['states']))
                    if 'states' in settings
                    else []
                ),
                transitions=(
                    list(map(Transition.create, settings['transitions']))
                    if 'transitions' in settings
                    else []
                ),
                on_entry=(
                    tuple(map(Action.create, tuplize(settings['on_entry'])))
                    if 'on_entry' in settings
                    else None
                ),
                on_exit=(
                    tuple(map(Action.create, tuplize(settings['on_exit'])))
                    if 'on_exit' in settings
                    else []
                ),
            )
        elif isinstance(settings, str):
            obj = State(settings)
        if obj:
            if hasattr(obj, 'transitions'):
                for transition in obj.transitions:
                    transition.source = obj
            return obj
        raise InvalidConfig('could not create state from provided settings')

    # @property
    # def datamodel(self) -> DataModel:
    #     """Get datamodel data items."""
    #     return self.__datamodel

    @property
    def path(self) -> str:
        """Get the statepath of this state."""
        return '.'.join(reversed([x.name for x in reversed(self)]))

    @property
    def type(self) -> str:
        """Get state type."""
        return self.__type

    @property
    def parent(self) -> Optional[SubstateMixin]:
        """Get parent state."""
        return self.__parent

    @parent.setter
    def parent(self, state: SubstateMixin) -> None:
        if self.__parent is None:
            self.__parent = state
        else:
            raise SuperstateException('cannot change parent for state')

    def run_on_entry(self, ctx: StateChart) -> Optional[Any]:
        """Run on-entry tasks."""

    def run_on_exit(self, ctx: StateChart) -> Optional[Any]:
        """Run on-exit tasks."""

    def validate(self) -> None:
        """Validate the current state configuration."""
        log.info("completed validation for state %s", self.name)

    # ancestors
    # descendents


class PseudoState(State):
    """Provide state for statechart."""

    def run_on_entry(self, ctx: StateChart) -> Optional[Any]:
        """Run on-entry tasks."""
        raise InvalidTransition('cannot transition to pseudostate')

    def run_on_exit(self, ctx: StateChart) -> Optional[Any]:
        """Run on-exit tasks."""
        raise InvalidTransition('cannot transition from pseudostate')


# class ConditionState(PseudoState, TransitionMixin):
#     """A pseudostate that only transits to other states."""
#
#     def __init__(self, name: str, **kwargs: Any) -> None:
#         """Initialize atomic state."""
#         self.transitions = kwargs.pop('transitions', [])
#         super().__init__(name, **kwargs)


class HistoryState(TransitionMixin, PseudoState):
    """A pseudostate that remembers transition history of compound states."""

    __kind: str = cast(str, Selection('deep', 'shallow'))

    def __init__(self, name: str, **kwargs: Any) -> None:
        self.__kind = kwargs.get('type', 'shallow')
        self.transitions = kwargs.pop('transitions', [])
        super().__init__(name, **kwargs)

    @property
    def type(self) -> str:
        """Return previous substate."""
        # TODO: implement tail for shallow history
        return self.__kind

    def validate(self) -> None:
        """Validate state to ensure conformance with type requirements."""
        # Transition must not contain 'cond' attributes.
        for transition in self.transitions:
            if transition.cond is not None:
                raise InvalidConfig(
                    'initial transition must not contain "cond" attribute'
                )
            # Transition must not contain 'event' attributes.
            if transition.event != '':
                raise InvalidConfig(
                    'initial transition must not contain "event" attribute'
                )
        super().validate()


class InitialState(TransitionMixin, PseudoState):
    """A pseudostate that provides the initial transition of compound state."""

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialize atomic state."""
        self.transitions = kwargs.pop('transitions', [])
        super().__init__(name, **kwargs)

    @classmethod
    def create(
        cls, settings: Union[State, dict, str]
    ) -> Union[SubstateMixin, State]:
        """Create state from configuration."""
        obj = None
        if isinstance(settings, InitialState):
            obj = settings
        elif isinstance(settings, dict):
            obj = settings.pop('factory', State)(
                name=settings.get('name', 'initial'),
                transitions=(
                    list(map(Transition.create, settings['transitions']))
                    if 'transitions' in settings
                    else []
                ),
            )
        elif isinstance(settings, str):
            obj = InitialState(
                name='initial', transitions=[Transition(target=settings)]
            )
        if obj:
            return obj
        raise InvalidConfig('could not create state from provided settings')

    @property
    def transition(self) -> Transition:
        """Return transition of initial state."""
        return self.transitions[0]

    def validate(self) -> None:
        """Validate state to ensure conformance with type requirements."""
        if len(self.transitions) != 1:
            raise InvalidConfig('initial state must contain one transition')
        # Transition must specify non-empty target.
        if self.transition.target == '':
            raise InvalidConfig(
                'initial transition must specify non-empty "target" attribute'
            )
        # Transition must not contain 'cond' attributes.
        if self.transition.cond is not None:
            raise InvalidConfig(
                'initial transition must not contain "cond" attribute'
            )
        # Transition must not contain 'event' attributes.
        if self.transition.event != '':
            raise InvalidConfig(
                'initial transition must not contain "event" attribute'
            )
        # Transition may contain executable content.
        super().validate()


class FinalState(ContentMixin, PseudoState):
    """Provide final state for a statechart."""

    def __init__(self, name: str, **kwargs: Any) -> None:
        # if 'donedata' in kwargs:
        #     self.__data = kwargs.pop('donedata')
        self.on_entry = kwargs.pop('on_entry')
        super().__init__(name, **kwargs)

    # def run_on_entry(self, ctx: StateChart) -> Optional[Any]:
    #   NOTE: SCXML Processor MUST generate the event done.state.id after
    #   completion of the <onentry> elements

    def run_on_exit(self, ctx: StateChart) -> Optional[Any]:
        raise InvalidTransition('final state cannot transition once entered')


class AtomicState(ContentMixin, TransitionMixin, State):
    """Provide an atomic state for a statechart."""

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialize atomic state."""
        self.on_entry = kwargs.pop('on_entry', None)
        self.on_exit = kwargs.pop('on_exit', None)
        self.transitions = kwargs.pop('transitions', [])
        super().__init__(name, **kwargs)

    def run_on_entry(self, ctx: StateChart) -> Optional[Any]:
        if self.datamodel.binding == 'late' and not hasattr(
            self.datamodel, 'maps'
        ):
            self.datamodel.populate()
        log.info("executing 'on_entry' state change actions for %s", self.name)
        results = super().run_on_entry(ctx)
        # process transient states
        for transition in self.transitions:
            if transition.event == '':
                ctx.trigger(transition.event)
                break
        return results


class SubstateMixin(State):
    """Provide composite abstract to define nested state types."""

    __states: dict[str, State] = {}

    def __getattr__(self, name: str) -> Any:
        if name.startswith('__'):
            raise AttributeError
        for key in self.states:
            if key == name:
                return self.states[name]
        raise AttributeError

    @property
    def states(self) -> dict[str, State]:
        """Return states."""
        return self.__states

    @states.setter
    def states(self, states: list[State]) -> None:
        """Define states."""
        if not self.__states:
            self.__states = {}
            for state in states:
                state.parent = self
                self.__states[state.name] = state

    def add_state(self, state: State) -> None:
        """Add substate to this state."""
        state.parent = self
        self.__states[state.name] = state

    def get_state(self, name: str) -> Optional[State]:
        """Get state by name."""
        return self.states.get(name)

    # ancestors = states
    children = states
    descendants = states


# class SubstateMixin(State):
#     """Provide composite abstract to define nested state types."""
#
#     __states: list[State] = []
#
#     def __getattr__(self, name: str) -> Any:
#         if name.startswith('__'):
#             raise AttributeError
#         state = self.get_state(name)
#         if state is not None:
#             return self.state
#         raise AttributeError
#
#     @property
#     def states(self) -> list[State]:
#         """Return states."""
#         return self.__states
#
#     @states.setter
#     def states(self, states: list[State]) -> None:
#         """Define states."""
#         if not self.__states:
#             for state in states:
#                 self.add_state(state)
#
#     def add_state(self, state: State) -> None:
#         """Add substate to this state."""
#         state.parent = self
#         self.__states.append(state)
#
#     def get_state(self, name: str) -> Optional[State]:
#         """Get state by name."""
#         for state in self.states:
#             if state.name == name:
#                 return state
#         return None
#
#     # ancestors = states
#     children = states
#     descendants = states


class CompoundState(SubstateMixin, AtomicState):
    """Provide nested state capabilitiy."""

    initial: Initial
    final: FinalState

    def __init__(self, name: str, **kwargs: Any) -> None:
        # self.__current = self
        self.initial = kwargs.pop('initial')
        self.states = kwargs.pop('states', [])
        super().__init__(name, **kwargs)

    def run_on_entry(self, ctx: StateChart) -> Optional[tuple[Any, ...]]:
        # if next(
        #     (x for x in self.states if isinstance(x, HistoryState)), False
        # ):
        #     ...
        # XXX: initial can be None
        if not self.initial:
            # if initial is None default is first child
            raise InvalidConfig('an initial state must exist for statechart')
        # TODO: deprecate callable initial state
        if self.initial:
            initial = (
                self.initial(ctx) if callable(self.initial) else self.initial
            )
            if initial and ctx.current_state != initial:
                ctx.change_state(initial)
        results: list[Any] = []
        results += filter(None, [super().run_on_entry(ctx)])
        # XXX: self transitions should still be possible here
        if (
            hasattr(ctx.current_state, 'initial')
            and ctx.current_state.initial
            and ctx.current_state.initial != ctx.current_state
        ):
            ctx.change_state(ctx.current_state.initial)
        return tuple(results) if results else None

    def validate(self) -> None:
        """Validate state to ensure conformance with type requirements."""
        if len(self.states) < 1:
            raise InvalidConfig('There must be one or more states')
        super().validate()


class ParallelState(SubstateMixin, AtomicState):
    """Provide parallel state capability for statechart."""

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialize compound state."""
        self.states = kwargs.pop('states', [])
        super().__init__(name, **kwargs)

    def run_on_entry(self, ctx: StateChart) -> Optional[Any]:
        results = []
        results.append(super().run_on_entry(ctx))
        for state in reversed(self.states.values()):
            results.append(state.run_on_entry(ctx))
        return results

    def run_on_exit(self, ctx: StateChart) -> Optional[Any]:
        results = []
        for state in reversed(self.states.values()):
            results.append(state.run_on_exit(ctx))
        results.append(super().run_on_exit(ctx))
        return results

    def validate(self) -> None:
        # TODO: empty statemachine should default to null event
        if self.type == 'compound':
            if len(self.__states) < 2:
                raise InvalidConfig('There must be at least two states')
            if not self.initial:
                raise InvalidConfig('There must exist an initial state')
        if self.initial and self.type == 'parallel':
            raise InvalidConfig(
                'parallel state should not have an initial state'
            )
        super().validate()
