"""Test transitions."""

import pytest

from superstate import (
    # InvalidTransition,
    StateChart,
)


class MyMachine(StateChart):
    """Provide statechart to verify transitions."""

    __state__ = {
        'initial': 'created',
        'states': [
            {
                'name': 'created',
                'transitions': [
                    {'event': 'queue', 'target': 'waiting'},
                    {'event': 'cancel', 'target': 'cancelled'},
                ],
            },
            {
                'name': 'waiting',
                'transitions': [
                    {'event': 'process', 'target': 'processed'},
                    {'event': 'cancel', 'target': 'cancelled'},
                ],
            },
            {'name': 'processed'},
            {'name': 'cancelled'},
        ],
    }


def test_its_declaration_creates_a_method_with_its_name():
    machine = MyMachine()
    assert hasattr(machine.state, 'queue') and callable(machine.state.queue)
    assert hasattr(machine.state, 'cancel') and callable(machine.state.cancel)
    machine.trigger('queue')


def test_it_changes_machine_state():
    machine = MyMachine()
    assert machine.state == 'created'
    machine.trigger('queue')
    assert machine.state == 'waiting'
    machine.trigger('process')
    assert machine.state == 'processed'


def test_it_transitions_machine_state():
    machine = MyMachine()
    assert machine.state == 'created'
    machine.trigger('queue')
    assert machine.state == 'waiting'
    machine.trigger('process')
    assert machine.state == 'processed'


# XXX: invalid transition errors are local to state because of getattr
def test_it_ensures_event_order():
    machine = MyMachine()
    assert machine.state == 'created'
    with pytest.raises(Exception):
        machine.trigger('process')

    # with pytest.raises(InvalidTransition):

    machine.trigger('queue')
    assert machine.state == 'waiting'
    # waiting does not have queue transition
    with pytest.raises(Exception):
        machine.trigger('queue')

    # with pytest.raises(InvalidTransition):

    machine.trigger('process')
    assert machine.state == 'processed'
    # cannot cancel after processed
    with pytest.raises(Exception):
        machine.trigger('cancel')


def test_it_accepts_multiple_origin_states():
    machine = MyMachine(initial='processed')
    assert machine.state == 'processed'
    with pytest.raises(Exception):
        machine.trigger('cancel')

    machine = MyMachine(initial='cancelled')
    assert machine.state == 'cancelled'
    with pytest.raises(Exception):
        machine.trigger('queue')

    machine = MyMachine(initial='waiting')
    machine.trigger('process')
    assert machine.state == 'processed'
    with pytest.raises(Exception):
        machine.trigger('cancel')
