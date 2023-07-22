import pytest

from superstate import InvalidTransition, StateChart, state


class Machine(StateChart):
    __superstate__ = state(
        {
            'name': 'engine',
            'initial': 'stopped',
            'states': [
                {
                    'name': 'started',
                    'transitions': [
                        {'event': 'restart', 'target': 'started'},
                        {'event': 'stop', 'target': 'stopped'},
                    ],
                },
                {'name': 'stopped', 'type': 'final'},
            ],
            'transitions': [{'target': 'started'}],
        }
    )


machine = Machine()


def test_auto_trigger():
    assert machine.initial == 'stopped'
    assert machine.state == 'started'


def test_self_trigger():
    machine.trigger('restart')
    assert machine.state == 'started'


def test_final_trigger():
    machine.trigger('stop')
    assert machine.state.type == 'final'
    with pytest.raises(InvalidTransition):
        machine.trigger('sabotage')
