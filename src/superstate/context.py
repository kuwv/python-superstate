"""Provide context for distributing settings within statechart."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, List, Tuple
from uuid import UUID

from superstate.state import ParallelState

if TYPE_CHECKING:
    from superstate.state import (
        # AtomicState,
        # SubstateMixin,
        # CompoundState,
        State,
    )


class Context:
    """Provide context for statechart."""

    def __init__(self, root: State) -> None:
        """Initialize a statechart from root state."""
        self.__sessionid = UUID(
            bytes=os.urandom(16), version=4  # pylint: disable=no-member
        )
        self.__root = root
        self.__current_state = self.__root

    @property
    def _sessionid(self) -> str:
        """Return the current state."""
        return str(self.__sessionid)

    @property
    def current_state(self) -> State:
        """Return the current state."""
        # TODO: rename to "head" or "position"
        return self.__current_state

    @current_state.setter
    def current_state(self, state: State) -> None:
        """Return the current state."""
        # TODO: rename to "head" or "position"
        self.__current_state = state

    @property
    def root(self) -> State:
        """Return root state of statechart."""
        return self.__root

    @property
    def parent(self) -> State:
        """Return parent."""
        return self.current_state.parent or self.root

    @property
    def children(self) -> Tuple[State, ...]:
        """Return list of states."""
        return (
            tuple(self.__current_state.states.values())
            if hasattr(self.__current_state, 'states')
            else ()
        )

    @property
    def states(self) -> Tuple[State, ...]:
        """Return list of states."""
        return tuple(self.parent.states.values())

    @property
    def siblings(self) -> Tuple[State, ...]:
        """Return list of states."""
        return tuple(self.parent.states.values())

    @property
    def active(self) -> Tuple[State, ...]:
        """Return active states."""
        states: List[State] = []
        parents = list(reversed(self.current_state))
        for i, x in enumerate(parents):
            n = i + 1
            if not n >= len(parents) and isinstance(parents[n], ParallelState):
                states += list((parents[n]).states)  # type: ignore
            else:
                states.append(x)
        return tuple(states)
