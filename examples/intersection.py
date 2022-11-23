"""Demonstrate a stoplight."""

import time

from superstate import StateChart, State, create_machine


def get_stoplight(name: str, initial: str = 'red') -> State:
    return __machine__ = create_machine(
        {
            'name': name,
            'initial': initial,
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
                    'on_entry': lambda: print('Red Light!'),
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
                            'action': lambda: time.sleep(2),
                        }
                    ],
                    'on_entry': lambda: print('Green light!'),
                },
            ],
        }
    )


class Intersection(StateChart):
    """Provide an object representing an intersection."""

    __machine__ = create_machine(
        {
            'name': 'intersection',
            'kind': 'parallel',
            'states': [
                get_stoplight('north_sourth', 'red'),
                get_stoplight('east_west', 'green'),
            ],
        }
    )

    def _change_red(self) -> None:
        print(f"turning intersection {self.state} red")
        if self.state:
            self.turn_yellow()
            self.turn_red()
        else:
            raise Exception('missing stoplight')

    def _change_green(self) -> None:
        print(f"turning intersection {self.state} green")
        if self.state:
            self.turn_green()
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
    for x in range(1, 5):
        print(intersection.state)
        intersection.change_light()
