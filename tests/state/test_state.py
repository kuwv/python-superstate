# import pytest

from superstate import StateChart, state


def test_it_defines_states():
    class MyMachine(StateChart):
        __superstate__ = state(
            {
                'initial': 'read',
                'states': [
                    {'name': 'unread'},
                    {'name': 'read'},
                    {'name': 'closed'},
                ],
            }
        )

    machine = MyMachine()
    assert len(machine.states) == 3
    assert machine.states == ('unread', 'read', 'closed')


def test_it_has_an_initial():
    class MyMachine(StateChart):
        __superstate__ = state(
            {
                'initial': 'closed',
                'states': [{'name': 'open'}, {'name': 'closed'}],
            }
        )

    machine = MyMachine()
    assert machine.superstate.initial == 'closed'
    assert machine.state == 'closed'


def test_it_defines_states_using_method_calls():
    class MyMachine(StateChart):
        __superstate__ = state(
            {
                'initial': 'unread',
                'states': [
                    {
                        'name': 'unread',
                        'transitions': [{'event': 'read', 'target': 'read'}],
                    },
                    {
                        'name': 'read',
                        'transitions': [
                            {'event': 'close', 'target': 'closed'}
                        ],
                    },
                    {'name': 'closed'},
                ],
            }
        )

    machine = MyMachine()
    assert len(machine.states) == 3
    assert machine.states == ('unread', 'read', 'closed')

    class OtherMachine(StateChart):
        __superstate__ = state(
            {
                'initial': 'idle',
                'states': [
                    {
                        'name': 'idle',
                        'transitions': [
                            {'event': 'work', 'target': 'working'}
                        ],
                    },
                    {'name': 'working'},
                ],
            }
        )

    machine = OtherMachine()
    assert len(machine.states) == 2
    assert machine.states == ('idle', 'working')


def test_its_initial_may_be_a_callable():
    def is_business_hours():
        """Set attribute that is used by initial callable."""
        return True

    class Person(StateChart):
        __superstate__ = state(
            {
                'initial': (
                    lambda person: (person.working and is_business_hours())
                    and 'awake'
                    or 'sleeping'
                ),
                'states': [{'name': 'awake'}, {'name': 'sleeping'}],
            }
        )

        def __init__(self, working):
            self.working = working
            super().__init__()

    person = Person(working=True)
    assert person.state == 'awake'

    person = Person(working=False)
    assert person.state == 'sleeping'
