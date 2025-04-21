"""Provide superstate transition capabilities."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Callable, Optional, Union, cast

from superstate.exception import InvalidConfig, SuperstateException
from superstate.model import Action, Conditional
from superstate.types import Selection, Identifier
from superstate.utils import tuplize

if TYPE_CHECKING:
    from superstate.machine import StateChart
    from superstate.state import State
    from superstate.types import ActionTypes

log = logging.getLogger(__name__)

TRANSITION_PATTERN = r'^(([a-zA-Z][a-zA-Z0-9:\.\-_]*(\.\*)?)|(\.|\*))?$'


class Transition:
    """Represent statechart transition.

    [Definition: A transition matches an event if at least one of its event
    descriptors matches the event's name.]

    [Definition: An event descriptor matches an event name if its string of
    tokens is an exact match or a prefix of the set of tokens in the event's
    name. In all cases, the token matching is case sensitive.]
    """

    # __slots__ = ['event', 'target', 'content', 'cond', 'type']

    __source: Optional[State] = None
    event: str = cast(str, Identifier(TRANSITION_PATTERN))
    cond: Optional['ActionTypes']
    target: str = cast(str, Identifier(TRANSITION_PATTERN))
    type: str = cast(str, Selection('internal', 'external'))
    content: Optional['ActionTypes']

    def __init__(
        self,
        # settings: Optional[Dict[str, Any]] = None,
        # /,
        **kwargs: Any,
    ) -> None:
        """Transition from one state to another."""
        # https://www.w3.org/TR/scxml/#events
        self.event = kwargs.get('event', '')
        self.cond = kwargs.get('cond')  # XXX: should default to bool
        self.target = kwargs.get('target', '')
        self.type = kwargs.get('type', 'internal')
        self.content = kwargs.get('content')

    def __repr__(self) -> str:
        return repr(f"Transition(event={self.event}, target={self.target})")

    @classmethod
    def create(cls, settings: Union[Transition, dict]) -> Transition:
        """Create transition from configuration."""
        if isinstance(settings, Transition):
            return settings
        if isinstance(settings, dict):
            # print(settings['content'] if 'content' in settings else None)
            return cls(
                event=settings.get('event', ''),
                cond=(
                    tuple(map(Conditional.create, tuplize(settings['cond'])))
                    if 'cond' in settings
                    else []
                ),
                target=settings.get('target', ''),
                type=settings.get('type', 'internal'),
                content=(
                    tuple(map(Action.create, tuplize(settings['content'])))
                    if 'content' in settings
                    else []
                ),
            )
        raise InvalidConfig('could not find a valid transition configuration')

    @property
    def source(self) -> Optional[State]:
        """Get source state."""
        return self.__source

    @source.setter
    def source(self, state: State) -> None:
        if self.__source is None:
            self.__source = state
        else:
            raise SuperstateException('cannot change source of transition')

    def execute(
        self, ctx: StateChart, *args: Any, **kwargs: Any
    ) -> Optional[List[Any]]:
        """Transition the state of the statechart."""
        log.info("executing transition contents for event %r", self.event)
        results: Optional[List[Any]] = None
        if self.content:
            results = []
            provider = ctx.datamodel.provider(ctx)
            for expression in tuplize(self.content):
                results.append(provider.handle(expression, *args, **kwargs))
        log.info("completed transition contents for event %r", self.event)
        relpath = ctx.get_relpath(self.target)
        if relpath == '.':  # handle self transition
            ctx.current_state.run_on_exit(ctx)
            ctx.current_state.run_on_entry(ctx)
        else:
            macrostep = relpath.split('.')[2 if relpath.endswith('.') else 1 :]
            while macrostep[0] == '':  # reverse
                ctx.current_state.run_on_exit(ctx)
                ctx.current_state = ctx.active[1]
                macrostep.pop(0)
            for microstep in macrostep:  # forward
                try:
                    if (
                        # isinstance(ctx.current_state, State)
                        hasattr(ctx.current_state, 'states')
                        and microstep in ctx.current_state.states
                    ):
                        state = ctx.get_state(microstep)
                        ctx.current_state = state
                        state.run_on_entry(ctx)
                    else:
                        raise InvalidState(
                            f"statepath not found: {self.target}"
                        )
                except SuperstateException as err:
                    log.error(err)
                    raise KeyError('superstate is undefined') from err
        log.info('changed state to %s', self.target)
        return results

    def evaluate(self, ctx: StateChart, *args: Any, **kwargs: Any) -> bool:
        """Evaluate conditionss of transition."""
        result = True
        if self.cond:
            provider = ctx.datamodel.provider(ctx)
            for expression in tuplize(self.cond):
                result = provider.handle(expression, *args, **kwargs)
                if result is False:
                    break
        return result
