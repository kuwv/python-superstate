"""Demonstrate a stoplight."""

import time
from typing import Callable, Union

from superstate import StateChart, State, Transition


class StopLight(State):
    """Provide representation of a stoplight."""

    def __init__(self, name: str, initial: Union[Callable, str]) -> None:
        super().__init__(
            name=name,
            initial=initial,
            states=[
                State(
                    name='red',
                    transitions=[
                        Transition(
                            event='turn_green',
                            target='green',
                            action=lambda: time.sleep(5),
                        )
                    ],
                    on_entry=lambda: print('Red Light!'),
                ),
                State(
                    name='yellow',
                    transitions=[
                        Transition(
                            event='turn_red',
                            target='red',
                            action=lambda: time.sleep(5),
                        )
                    ],
                    on_entry=lambda: print('Yellow light!'),
                ),
                State(
                    name='green',
                    transitions=[
                        Transition(
                            event='turn_yellow',
                            target='yellow',
                            action=lambda: time.sleep(2),
                        )
                    ],
                    on_entry=lambda: print('Green light!'),
                ),
            ],
            on_entry=lambda: print('entered intersection'),
        )


class Intersection(StateChart):
    """Provide an object representing an intersection."""

    __state__ = State(
        name='intersection',
        type='parallel',
        states=[
            StopLight('north_south', 'red'),
            StopLight('east_west', 'green'),
        ],
    )

    def __change_light(self, active: str, inactive: str) -> None:
        self.trigger('turn_yellow', statepath=f"intersection.{active}.green")
        self.trigger('turn_red', statepath=f"intersection.{active}.yellow")
        self.trigger('turn_green', statepath=f"intersection.{inactive}.red")

    def change_light(self) -> None:
        """Start timing length of red light."""
        print('state', self.north_south.state, self.east_west.state)

        assert self.is_north_south is True
        assert self.is_east_west is True
        assert self.is_nothing is False

        if self.north_south.state == 'green':
            self.__change_light(active='north_south', inactive='east_west')

        if self.east_west.state == 'green':
            self.__change_light(active='east_west', inactive='north_south')
            # self.east_west.green.turn_yellow()
            # self.east_west.yellow.turn_red()
            # self.north_south.red.turn_green()


if __name__ == '__main__':
    intersection = Intersection(logging_enabled=True, logging_level='debug')

    assert intersection.north_south.state == 'green'

    for x in range(1, 5):
        intersection.change_light()
