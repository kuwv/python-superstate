"""Provide superstate transition capabilities."""

import logging
from typing import TYPE_CHECKING, Any, Callable, Optional

# from superstate.models import NameDescriptor
from superstate.trigger import Action, Guard

if TYPE_CHECKING:
    from superstate.machine import StateChart
    # from superstate.state import State
    from superstate.types import EventActions, GuardConditions

log = logging.getLogger(__name__)


class Transition:
    """Represent statechart transition."""

    # __slots__ = ['event', 'target', 'action', 'cond']
    # event = cast(str, NameDescriptor())
    # target = cast(str, NameDescriptor())

    def __init__(
        self,
        event: str,
        target: str,  # XXX target can be self-transition
        action: Optional['EventActions'] = None,
        cond: Optional['GuardConditions'] = None,
        # kind: str = 'internal',
    ) -> None:
        """Transition from one state to another."""
        # https://www.w3.org/TR/scxml/#events
        self.event = event
        self.target = target
        self.action = action
        self.cond = cond
        # self.kind = kind

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
        ctx.change_state(target)
        if self.action:
            log.info("executed action event for %r", self.event)
            return Action(ctx)(self.action, *args, **kwargs)
        log.info("no action event for %r", self.event)
        return None

    def __repr__(self) -> str:
        return repr(f"Transition(event={self.event}, target={self.target})")

    def callback(self) -> Callable:
        """Provide callback from parent state when transition is called."""

        def event(ctx: 'StateChart', *args: Any, **kwargs: Any) -> None:
            """Provide callback event."""
            ctx.process_transitions(self.event, *args, **kwargs)

        event.__name__ = self.event
        event.__doc__ = f"Transition event: '{self.event}'."
        return event

    def evaluate(
        self, ctx: 'StateChart', *args: Any, **kwargs: Any
    ) -> bool:
        """Evaluate guards of transition."""
        return (
            Guard(ctx)(self.cond, *args, **kwargs)
            if self.cond
            else True
        )
