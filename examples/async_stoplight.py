"""Demonstrate a stoplight."""

import asyncio

from fluidstate import StateChart, State, Transition, states, transitions


class StopLight(StateChart):
    """Proide an object representing a stoplight."""

    states(
        State(
            'red',
            transitions=transitions(
                Transition(
                    'turn_green',
                    target='green',
                    action=lambda: asyncio.sleep(5),
                )
            ),
            on_entry=lambda: print('Red light!'),
        ),
        State(
            'yellow',
            transitions=transitions(
                Transition(
                    'turn_red',
                    target='red',
                    action=lambda: asyncio.sleep(5),
                )
            ),
            on_entry=lambda: print('Yellow light!'),
        ),
        State(
            'green',
            transitions=transitions(
                Transition(
                    'turn_yellow',
                    target='yellow',
                    action=lambda: asyncio.sleep(2),
                )
            ),
            on_entry=lambda: print('Green light!'),
        ),
    )

    initial: str = 'red'


if __name__ == '__main__':
    stoplight = StopLight()
    while True:
        stoplight.turn_green()
        stoplight.turn_yellow()
        stoplight.turn_red()
