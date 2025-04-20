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

    # __slots__ = ['event', 'target', 'action', 'cond', 'type']

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

    def __call__(
        self, ctx: StateChart, *args: Any, **kwargs: Any
    ) -> Optional[Any]:
        """Run transition process."""
        # TODO: move change_state to process_transitions
        if 'statepath' in kwargs:
            superstate_path = kwargs['statepath'].split('.')[:-1]
            target = (
                '.'.join(superstate_path + [self.target])
                if superstate_path != []
                else self.target
            )
        else:
            target = self.target

        results = None
        if self.content:
            results = []
            provider = ctx.datamodel.provider(ctx)
            for expression in tuplize(self.content):
                results.append(provider.handle(expression, *args, **kwargs))
            log.info("executed action event for %r", self.event)
        ctx.change_state(target)
        log.info("no action event for %r", self.event)
        return results

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

    def callback(self) -> Callable:
        """Provide callback from source state when transition is called."""

        def event(ctx: StateChart, *args: Any, **kwargs: Any) -> None:
            """Provide callback event."""
            ctx.process_transitions(self.event, *args, **kwargs)

        event.__name__ = self.event
        event.__doc__ = f"Transition event: '{self.event}'"
        return event

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
