"""Demonstrate auto-transition."""

from superstate import StateChart, state


class Machine(StateChart):
    """Example machine that will auto-transition on entry."""

    __superstate__ = state(
        {
            'name': 'engine',
            'initial': 'engine',
            'states': [
                {
                    'name': 'started',
                    'transitions': [
                        {'event': 'stop', 'target': 'stopped'},
                    ],
                    'on_entry': lambda: print('started'),
                },
                {
                    'name': 'stopped',
                    'transitions': [
                        {'event': 'start', 'target': 'started'},
                        {'event': 'fix', 'target': 'maintenance.disassembled'},
                    ],
                    'on_entry': lambda: print('stopped'),
                },
                {
                    'name': 'maintenance',
                    'states': [
                        {
                            'name': 'disassembled',
                            'transitions': [
                                {
                                    'event': 'check',
                                    'target': 'maintenance.checking',
                                }
                            ],
                            'on_entry': lambda: print('take apart'),
                        },
                        {
                            'name': 'checking',
                            'on_entry': lambda: print('checking'),
                        },
                    ],
                    'on_entry': lambda: print('fixing'),
                },
            ],
            'transitions': [
                {
                    'event': '',
                    'target': 'started',
                },
            ],
        }
    )


if __name__ == '__main__':
    machine = Machine(logging_enabled=True, logging_level='debug')
    # machine = Machine()
    assert machine.states == ('started', 'stopped', 'maintenance')
    # print(machine.transitions)

    # print('state', machine.state)
    assert machine.superstate.initial == 'engine'
    assert machine.state == 'started'

    machine.trigger('stop')
    machine.trigger('fix')
    # machine.trigger('fix')
    assert machine.state == 'disassembled'
    machine.trigger('check')
    assert machine.state == 'checking'
