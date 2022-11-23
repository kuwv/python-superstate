"""Demonstrate a stoplight."""

import asyncio

from superstate import StateChart, State, Transition, create_machine

# XXX: somehow broke this but not sure if it ever worked


class StopLight(StateChart):
    """Proide an object representing a stoplight."""

    __machine__ = create_machine(
        {
            'initial': 'red',
            'states': [
                State(
                    'red',
                    transitions=[
                        Transition(
                            'turn_green',
                            target='green',
                            action=lambda: asyncio.sleep(5),
                        )
                    ],
                    on_entry=lambda: print('Red light!'),
                ),
                State(
                    'yellow',
                    transitions=[
                        Transition(
                            'turn_red',
                            target='red',
                            action=lambda: asyncio.sleep(5),
                        )
                    ],
                    on_entry=lambda: print('Yellow light!'),
                ),
                State(
                    'green',
                    transitions=[
                        Transition(
                            'turn_yellow',
                            target='yellow',
                            action=lambda: asyncio.sleep(2),
                        )
                    ],
                    on_entry=lambda: print('Green light!'),
                ),
            ],
        }
    )


if __name__ == '__main__':
    stoplight = StopLight()
    while True:
        stoplight.turn_green()
        stoplight.turn_yellow()
        stoplight.turn_red()
