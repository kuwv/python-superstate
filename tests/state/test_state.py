# import pytest

from superstate import StateChart


def test_it_defines_states():
    class MyMachine(StateChart):
        state = {
            'initial': 'read',
            'states': [
                {'name': 'unread'},
                {'name': 'read'},
                {'name': 'closed'},
            ],
        }

    machine = MyMachine()
    assert len(machine.states) == 3
    assert machine.states == ('unread', 'read', 'closed')


def test_it_has_an_initial():
    class MyMachine(StateChart):
        state = {
            'initial': 'closed',
            'states': [{'name': 'open'}, {'name': 'closed'}],
        }

    machine = MyMachine()
    assert machine.parent.initial == 'closed'
    assert machine.current_state == 'closed'


def test_it_defines_states_using_method_calls():
    class MyMachine(StateChart):
        state = {
            'initial': 'unread',
            'states': [
                {
                    'name': 'unread',
                    'transitions': [{'event': 'read', 'target': 'read'}],
                },
                {
                    'name': 'read',
                    'transitions': [{'event': 'close', 'target': 'closed'}],
                },
                {'name': 'closed'},
            ],
        }

    machine = MyMachine()
    assert len(machine.states) == 3
    assert machine.states == ('unread', 'read', 'closed')

    class OtherMachine(StateChart):
        state = {
            'initial': 'idle',
            'states': [
                {
                    'name': 'idle',
                    'transitions': [{'event': 'work', 'target': 'working'}],
                },
                {'name': 'working'},
            ],
        }

    machine = OtherMachine()
    assert len(machine.states) == 2
    assert machine.states == ('idle', 'working')


# TODO: switch to initial state with executable transition
# def test_its_initial_may_be_a_callable():
#     def is_business_hours():
#         """Set attribute that is used by initial callable."""
#         return True
#
#     class Person(StateChart):
#         state = {
#             'initial': (
#                 lambda person: (person.working and is_business_hours())
#                 and 'awake'
#                 or 'sleeping'
#             ),
#             'states': [{'name': 'awake'}, {'name': 'sleeping'}],
#         }
#
#         def __init__(self, working):
#             self.working = working
#             super().__init__()
#
#     person = Person(working=True)
#     assert person.current_state == 'awake'
#
#     person = Person(working=False)
#     assert person.current_state == 'sleeping'
