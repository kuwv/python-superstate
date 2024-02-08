"""Demonstrate a parallel statechart."""

from superstate import StateChart, state


class Intersection(StateChart):
    """Provide an example street intersection."""

    state = state(
        {
            # not a parallel machine
            'name': 'light',
            'initial': 'green',
            'states': [
                {
                    'name': 'green',
                    'transitions': [{'event': 'TIMER', 'target': 'yellow'}],
                },
                {
                    'name': 'yellow',
                    'transitions': [{'event': 'TIMER', 'target': 'red'}],
                },
                # nested parallel machine
                {
                    'name': 'red',
                    'type': 'parallel',
                    'states': [
                        {
                            'name': 'walk_sign',
                            'initial': 'solid',
                            'states': [
                                {
                                    'name': 'solid',
                                    'transitions': [
                                        {
                                            'event': 'COUNTDOWN',
                                            'target': 'flashing',
                                        }
                                    ],
                                },
                                {
                                    'name': 'flashing',
                                    'transitions': [
                                        {
                                            'event': 'STOP_COUNTDOWN',
                                            'target': 'solid',
                                        },
                                    ],
                                },
                            ],
                        },
                        {
                            'name': 'pedestrian',
                            'initial': 'walk',
                            'states': [
                                {
                                    'name': 'walk',
                                    'transitions': [
                                        {
                                            'event': 'COUNTDOWN',
                                            'target': 'wait',
                                        }
                                    ],
                                },
                                {
                                    'name': 'wait',
                                    'transitions': [
                                        {
                                            'event': 'STOP_COUNTDOWN',
                                            'target': 'stop',
                                        }
                                    ],
                                },
                                {'name': 'stop', 'type': 'final'},
                            ],
                        },
                    ],
                },
            ],
        }
    )


if __name__ == '__main__':
    intesection = Intersection()
