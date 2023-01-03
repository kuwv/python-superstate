"""Provide superstate transition capabilities."""

import logging
from typing import TYPE_CHECKING, Any, Callable, Optional

from superstate.exec import Action, Guard

if TYPE_CHECKING:
    from superstate.machine import StateChart
    from superstate.types import EventActions, GuardConditions

log = logging.getLogger(__name__)


class Transition:
    """Represent statechart transition."""

    __slots__ = ['event', 'target', 'action', 'cond']
    # event = cast(str, NameDescriptor())
    # target = cast(str, NameDescriptor())

    def __init__(
        self,
        event: str,
        target: str,
        action: Optional['EventActions'] = None,
        cond: Optional['GuardConditions'] = None,
    ) -> None:
        self.event = event
        self.target = target
        self.action = action
        self.cond = cond

    def __repr__(self) -> str:
        return repr(f"Transition(event={self.event}, target={self.target})")

    def callback(self) -> Callable:
        """Provide callback from parent state when transition is called."""

        def event(machine: 'StateChart', *args: Any, **kwargs: Any) -> None:
            """Provide callback event."""
            machine.process_transitions(self.event, *args, **kwargs)

        event.__name__ = self.event
        event.__doc__ = f"Show event: '{self.event}'."
        return event

    def evaluate(
        self, machine: 'StateChart', *args: Any, **kwargs: Any
    ) -> bool:
        """Evaluate guards of transition."""
        return (
            Guard(machine).evaluate(self.cond, *args, **kwargs)
            if self.cond
            else True
        )

    def run(self, machine: 'StateChart', *args: Any, **kwargs: Any) -> None:
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
        machine.change_state(target)
        if self.action:
            Action(machine).run(self.action, *args, **kwargs)
            log.info("executed action event for '{%s}'", self.event)
        else:
            log.info("no action event for '%s'", self.event)
