import pytest

from superstate import InvalidTransition, StateChart, state


class Machine(StateChart):
    __superstate__ = state(
        {
            'name': 'engine',
            'initial': 'engine',
            'states': [
                {
                    'name': 'started',
                    'transitions': [
                        {'event': 'restart', 'target': 'started'},
                        {'event': 'stop', 'target': 'stopped'},
                    ],
                },
                {'name': 'stopped', 'kind': 'final'},
            ],
            'transitions': [
                {
                    'event': '',
                    'target': 'started',
                },
            ],
        }
    )


machine = Machine()


def test_auto_trigger():
    assert machine.superstate.initial == 'engine'
    assert machine.state == 'started'


def test_self_trigger():
    machine.trigger('restart')
    assert machine.state == 'started'


def test_final_trigger():
    machine.trigger('stop')
    assert machine.state.kind == 'final'
    with pytest.raises(InvalidTransition):
        machine.trigger('sabotage')
