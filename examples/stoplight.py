"""Demonstrate a stoplight."""

import time

from superstate import StateChart, state


class StopLight(StateChart):
    """Proide an object representing a stoplight."""

    state = state(
        {
            'name': 'stoplight',
            'initial': 'red',
            'states': [
                {
                    'name': 'red',
                    'transitions': [
                        {
                            'event': 'turn_green',
                            'target': 'green',
                            'action': lambda: time.sleep(5),
                        }
                    ],
                    'on_entry': lambda: print('Red light!'),
                },
                {
                    'name': 'yellow',
                    'transitions': [
                        {
                            'event': 'turn_red',
                            'target': 'red',
                            'action': lambda: time.sleep(5),
                        }
                    ],
                    'on_entry': lambda: print('Yellow light!'),
                },
                {
                    'name': 'green',
                    'transitions': [
                        {
                            'event': 'turn_yellow',
                            'target': 'yellow',
                            'action': lambda: time.sleep(5),
                        }
                    ],
                    'on_entry': lambda: print('Green light!'),
                },
            ],
        }
    )


if __name__ == '__main__':
    stoplight = StopLight()
    for x in range(3):
        stoplight.turn_green()
        stoplight.turn_yellow()
        stoplight.turn_red()
