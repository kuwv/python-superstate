"""Demonstrate auto-transition."""

from superstate import StateChart


class Machine(StateChart):
    """Example machine that will auto-transition on entry."""

    state = {
        'name': 'engine',
        'initial': 'stopped',
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
                    {'event': 'fix', 'target': 'maintenance.fixing'},
                ],
                'on_entry': lambda: print('stopped'),
            },
            {
                'name': 'maintenance',
                'initial': 'checking',
                'states': [
                    {
                        'name': 'checking',
                        'on_entry': lambda: print('checking'),
                    },
                    {
                        'name': 'fixing',
                        'transitions': [
                            {
                                'event': 'check',
                                'target': 'maintenance.checking',
                            }
                        ],
                        'on_entry': lambda: print('take apart'),
                    },
                ],
                'on_entry': lambda: print('fixing'),
            },
        ],
        'transitions': [
            {
                'target': 'started',
                'cond': (
                    lambda ctx: hasattr(ctx, 'autostart') and ctx.autostart
                ),
            },
        ],
    }
    autostart: bool


if __name__ == '__main__':
    Machine.autostart = True
    machine = Machine(logging_enabled=True, logging_level='debug')
    # machine = Machine()
    assert machine.states == ('started', 'stopped', 'maintenance')
    # print(machine.transitions)

    # print('state', machine.state)
    assert machine.superstate.initial == 'stopped'
    assert machine.state == 'started'

    machine.trigger('stop')
    machine.trigger('fix')
    assert machine.state == 'fixing'
    machine.trigger('check')
    assert machine.state == 'checking'
