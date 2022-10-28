"""Demonstrate a stoplight."""

import time

from fluidstate import StateChart, State, Transition, states, transitions


class StopLight(StateChart):
    """Proide an object representing a stoplight."""

    initial: str = 'red'
    states(
        State(
            name='red',
            transitions=transitions(
                Transition(
                    event='turn_green',
                    target='green',
                    action=lambda: time.sleep(5),
                )
            ),
            on_entry=lambda: print('Red light!'),
        ),
        State(
            name='yellow',
            transitions=transitions(
                Transition(
                    event='turn_red',
                    target='red',
                    action=lambda: time.sleep(5),
                )
            ),
            on_entry=lambda: print('Yellow light!'),
        ),
        State(
            name='green',
            transitions=transitions(
                Transition(
                    event='turn_yellow',
                    target='yellow',
                    action=lambda: time.sleep(5),
                )
            ),
            on_entry=lambda: print('Green light!'),
        ),
    )


if __name__ == '__main__':
    stoplight = StopLight()
    for x in range(3):
        stoplight.turn_green()
        stoplight.turn_yellow()
        stoplight.turn_red()
