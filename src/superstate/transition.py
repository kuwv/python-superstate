"""Provide superstate transition capabilities."""

import logging
from typing import TYPE_CHECKING, Any, Callable, Optional, Union, cast

from superstate.exception import InvalidConfig
from superstate.types import Selection, Identifier
from superstate.utils import tuplize

if TYPE_CHECKING:
    from superstate.machine import StateChart
    from superstate.types import ActionTypes, ConditionTypes

log = logging.getLogger(__name__)

EVENT_PATTERN = r'^(([a-zA-Z][a-zA-Z0-9:\.\-_]*(\.\*)?)|\*)?$'


class Transition:
    """Represent statechart transition.

    [Definition: A transition matches an event if at least one of its event
    descriptors matches the event's name. ]

    [Definition: An event descriptor matches an event name if its string of
    tokens is an exact match or a prefix of the set of tokens in the event's
    name. In all cases, the token matching is case sensitive. ]
    """

    # __slots__ = ['event', 'target', 'action', 'cond', 'type']

    event: str = cast(str, Identifier(EVENT_PATTERN))
    target: str = cast(str, Identifier())
    actions: Optional['ActionTypes']
    cond: Optional['ConditionTypes']
    type: str = cast(str, Selection('internal', 'external'))

    def __init__(
        self,
        # settings: Optional[Dict[str, Any]] = None,
        # /,
        **kwargs: Any,
    ) -> None:
        """Transition from one state to another."""
        # https://www.w3.org/TR/scxml/#events
        self.event = kwargs.get('event', '')
        self.target = kwargs['target']
        self.actions = kwargs.get('actions')
        self.cond = kwargs.get('cond')
        self.type = kwargs.get('type', 'internal')

    @classmethod
    def create(cls, settings: Union['Transition', dict]) -> 'Transition':
        """Create transition from configuration."""
        if isinstance(settings, Transition):
            return settings
        if isinstance(settings, dict):
            return cls(
                event=settings.get('event', ''),
                target=settings['target'],  # XXX: should allow optional
                actions=settings.get('actions'),
                cond=settings.get('cond'),
                type=settings.get('type', 'internal'),
            )
        raise InvalidConfig('could not find a valid transition configuration')

    def __repr__(self) -> str:
        return repr(f"Transition(event={self.event}, target={self.target})")

    def __call__(
        self, ctx: 'StateChart', *args: Any, **kwargs: Any
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
        if self.actions:
            Executor = ctx._datamodel.executor if ctx._datamodel else None
            if Executor:
                executor = Executor(ctx)
                results = tuple(
                    executor.run(command, *args, **kwargs)
                    for command in tuplize(self.actions)
                )
                log.info("executed action event for %r", self.event)
        ctx.change_state(target)
        log.info("no action event for %r", self.event)
        return results

    def callback(self) -> Callable:
        """Provide callback from parent state when transition is called."""

        def event(ctx: 'StateChart', *args: Any, **kwargs: Any) -> None:
            """Provide callback event."""
            ctx.process_transitions(self.event, *args, **kwargs)

        event.__name__ = self.event
        event.__doc__ = f"Transition event: '{self.event}'"
        return event

    def evaluate(self, ctx: 'StateChart', *args: Any, **kwargs: Any) -> bool:
        """Evaluate conditionss of transition."""
        results = True
        if self.cond:
            Condition = ctx._datamodel.conditional if ctx._datamodel else None
            if Condition:
                conditions = Condition(ctx)
                for condition in tuplize(self.cond):
                    results = conditions.check(condition, *args, **kwargs)
                    if results is False:
                        break
        return results
