"""Test change notification."""

from typing import List, Tuple

from superstate import StateChart, Script, State, Transition


class Door(StateChart):
    """Represent a door."""

    state = State(
        name='door',
        initial='closed',
        states=[
            State(
                name='open',
                transitions=[
                    Transition(
                        event='close',
                        target='closed',
                        content=[
                            Script(
                                lambda ctx: ctx.state_trigger(
                                    source='open', target='closed'
                                )
                            )
                        ],
                    ),
                    Transition(
                        event='crack',
                        target='broken',
                        content=[
                            Script(
                                lambda ctx: ctx.state_trigger(
                                    source='open', target='crack'
                                )
                            )
                        ],
                    ),
                ],
            ),
            State(
                name='closed',
                transitions=[
                    Transition(
                        event='open',
                        target='open',
                        content=[
                            Script(
                                lambda ctx: ctx.state_trigger(
                                    source='closed', target='open'
                                )
                            )
                        ],
                    ),
                    Transition(
                        event='crack',
                        target='broken',
                        content=[
                            Script(
                                lambda ctx: ctx.state_trigger(
                                    source='crack', target='broken'
                                )
                            )
                        ],
                    ),
                ],
            ),
            State('broken'),
        ],
    )

    def __init__(self) -> None:
        super().__init__()
        self.state_changes: List[Tuple[str, str]] = []

    def state_trigger(self, source: str, target: str) -> None:
        """Record state changes using transition content."""
        self.state_changes.append((source, target))


def test_notify_state_changes() -> None:
    """Test notification of state changes."""
    door = Door()
    door.trigger('open')
    door.trigger('close')
    door.trigger('crack')
    assert door.state_changes == [
        ('closed', 'open'),
        ('open', 'closed'),
        ('crack', 'broken'),
    ]
