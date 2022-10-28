"""Demonstrate a stoplight."""

import time

from fluidstate import StateChart, State, states, transitions


class StopLight(StateChart):
    """Proide an object representing a stoplight."""

    states(
        State(
            'red',
            transitions=transitions(
                {
                    'event': 'turn_green',
                    'target': 'green',
                    'action': lambda: time.sleep(5),
                }
            ),
            on_entry=lambda: print('Red Light!'),
        ),
        State(
            'yellow',
            transitions=transitions(
                {
                    'event': 'turn_red',
                    'target': 'red',
                    'action': lambda: time.sleep(5),
                }
            ),
            on_entry=lambda: print('Yellow light!'),
        ),
        State(
            'green',
            transitions=transitions(
                {
                    'event': 'turn_yellow',
                    'target': 'yellow',
                    'action': lambda: time.sleep(2),
                }
            ),
            on_entry=lambda: print('Green light!'),
        ),
    )

    initial: str = 'red'


class Intersection(StateChart):
    """Provide an object representing an intersection."""

    states(
        State(
            'north_south',
            transitions=transitions(
                {
                    'event': 'allow_east_west',
                    'target': 'east_west',
                    'action': '_change_green',
                }
            ),
            on_exit='_change_red',
            machine=StopLight(),
        ),
        State(
            'east_west',
            transitions=transitions(
                {
                    'event': 'allow_north_south',
                    'target': 'north_south',
                    'action': '_change_green',
                }
            ),
            on_exit='_change_red',
            machine=StopLight(initial='green'),
        ),
    )

    initial: str = 'east_west'

    def _change_red(self) -> None:
        print(f"turning intersection {self.state} red")
        if self.state.machine:
            self.state.machine.turn_yellow()
            self.state.machine.turn_red()
        else:
            raise Exception('missing stoplight')

    def _change_green(self) -> None:
        print(f"turning intersection {self.state} green")
        if self.state.machine:
            self.state.machine.turn_green()
            self.change_light()
        else:
            raise Exception('missing stoplight')

    def change_light(self) -> None:
        """Start timing length of red light."""
        if self.state == 'north_south':
            print(intersection.state)
            self.allow_east_west()
        if self.state == 'east_west':
            print(intersection.state)
            self.allow_north_south()


if __name__ == '__main__':
    intersection = Intersection()
    intersection.change_light()
