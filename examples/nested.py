"""Demonstrate a nested."""

from superstate import StateChart, state


class Nested(StateChart):
    """Proide an object representing a nested."""

    __superstate__ = state(
        {
            'initial': 'start',
            'states': [
                {
                    'name': 'start',
                    'initial': 'inter_one',
                    'on_entry': lambda: print('start'),
                    'transitions': [
                        {
                            'event': 'change',
                            'target': 'start.inter_one',
                            'action': lambda: print(
                                'transitioning to inter_one'
                            ),
                        }
                    ],
                    'states': [
                        {
                            'name': 'inter_one',
                            'transitions': [
                                {
                                    'event': 'change',
                                    'target': 'start.inter_two',
                                    'action': lambda: print(
                                        'transitioning to inter_two'
                                    ),
                                }
                            ],
                            'on_entry': lambda: print('inter_one'),
                        },
                        {
                            'name': 'inter_two',
                            'initial': 'substate_one',
                            'states': [
                                {
                                    'name': 'substate_one',
                                    'transitions': [
                                        {
                                            'event': 'change',
                                            'target': 'end',
                                            'action': lambda: print(
                                                'transitioning to end'
                                            ),
                                        },
                                    ],
                                },
                            ],
                            'transitions': [
                                {
                                    'event': 'change',
                                    'target': 'start.inter_two.substate_one',
                                    'action': lambda: print(
                                        'transitioning to substate_one'
                                    ),
                                }
                            ],
                            'on_entry': lambda: print('inter_two'),
                        },
                    ],
                },
                {
                    'name': 'end',
                    'on_entry': lambda: print('StateChart ended!'),
                },
            ],
        }
    )


if __name__ == '__main__':
    nested = Nested(
        logging_enabled=True,
        logging_level='debug',
    )
    print('- initial:', nested.superstate.initial)
    print('- state:', nested.state)
    print('- states:', nested.states)
    print('- transitions:', nested.transitions)
    print('- end:', nested.get_state('end'))
    print('- get nested state:', nested.get_state('start.inter_two'))
    print(vars(nested.superstate))

    # # print(nested.becomming.name)
    for x in range(4):
        print(nested.superstate, nested.state.name, vars(nested.state))
        nested.trigger('change')
        print(nested.superstate, nested.state.name, vars(nested.state))
