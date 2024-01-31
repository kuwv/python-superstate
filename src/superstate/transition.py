"""Provide superstate transition capabilities."""

import logging
from typing import TYPE_CHECKING, Any, Callable, Optional, Union

from superstate.exception import InvalidConfig

# from superstate.model import NameDescriptor
from superstate.utils import tuplize

if TYPE_CHECKING:
    from superstate.machine import StateChart

    # from superstate.state import State
    from superstate.types import EventActions, GuardConditions

log = logging.getLogger(__name__)


class Transition:
    """Represent statechart transition.

    [Definition: A transition matches an event if at least one of its event
    descriptors matches the event's name. ]

    [Definition: An event descriptor matches an event name if its string of
    tokens is an exact match or a prefix of the set of tokens in the event's
    name. In all cases, the token matching is case sensitive. ]
    """

    # __slots__ = ['event', 'target', 'action', 'cond']
    # event = cast(str, NameDescriptor())
    # target = cast(str, NameDescriptor())

    def __init__(  # pylint: disable=too-many-arguments
        self,
        event: str,
        target: str,  # XXX target can be self-transition
        action: Optional['EventActions'] = None,  # TODO: switch to splat
        cond: Optional['GuardConditions'] = None,  # XXX: should default True
        kind: str = 'internal',
        # **kwargs: Any,
    ) -> None:
        """Transition from one state to another."""
        # https://www.w3.org/TR/scxml/#events
        self.event = event
        self.target = target
        self.action = action
        self.cond = cond
        self.type = kind
        self.actions: Optional['EventActions'] = None

    @classmethod
    def create(cls, settings: Union['Transition', dict]) -> 'Transition':
        """Create transition from configuration."""
        print('----------------------------')
        print(settings)
        if isinstance(settings, Transition):
            return settings
        if isinstance(settings, dict):
            return cls(
                event=settings.get('event', ''),
                target=settings['target'],  # XXX: should allow optional
                action=settings.get('action'),
                cond=settings.get('cond'),
                # kind=settings.get('type', 'internal'),
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
        if self.action:
            Executor = (
                ctx.datamodel.executor
                if ctx.datamodel and ctx.datamodel.executor
                else None
            )
            if Executor:
                log.info("executed action event for %r", self.event)
                executor = Executor(ctx)
                results = tuple(
                    executor.run(command, *args, **kwargs)
                    for command in tuplize(self.action)
                )
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
        """Evaluate guards of transition."""
        results = True
        if self.cond:
            GuardModel = (
                ctx.datamodel.conditional
                if ctx.datamodel and ctx.datamodel.conditional
                else None
            )
            if GuardModel:
                guard = GuardModel(ctx)
                for condition in tuplize(self.cond):
                    results = guard.check(condition, *args, **kwargs)
                    if results is False:
                        break
        return results
