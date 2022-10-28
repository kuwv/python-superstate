import unittest

from fluidstate import StateChart, State, Transition, states


class FluidState(unittest.TestCase):
    def test_it_defines_states(self):
        class MyMachine(StateChart):
            states(State('unread'), State('read'), State('closed'))
            initial = 'read'

        machine = MyMachine()
        assert len(machine.states) == 3
        assert machine.states == ['unread', 'read', 'closed']

    def test_it_has_an_initial(self):
        class MyMachine(StateChart):
            initial = 'closed'
            states(State('open'), State('closed'))

        machine = MyMachine()
        assert machine.initial == 'closed'
        assert machine.state == 'closed'

    def test_it_defines_states_using_method_calls(self):
        class MyMachine(StateChart):
            states(
                State(
                    'unread',
                    [Transition(event='read', target='read')],
                ),
                State(
                    'read',
                    [Transition(event='close', target='closed')],
                ),
                State('closed'),
            )
            initial = 'unread'

        machine = MyMachine()
        assert len(machine.states) == 3
        assert machine.states == ['unread', 'read', 'closed']

        class OtherMachine(StateChart):
            states(
                State(
                    'idle',
                    [Transition(event='work', target='working')],
                ),
                State('working'),
            )
            initial = 'idle'

        machine = OtherMachine()
        assert len(machine.states) == 2
        assert machine.states == ['idle', 'working']

    # FIXME: cannot use lamda initialization
    def test_its_initial_may_be_a_callable(self):
        def is_business_hours():
            return True

        class Person(StateChart):
            states(State('awake'), State('sleeping'))
            initial = (
                lambda person: (person.worker and is_business_hours())
                and 'awake'
                or 'sleeping'
            )

            def __init__(self, worker):
                self.worker = worker
                super().__init__()

        person = Person(worker=True)
        assert person.state == 'awake'

        person = Person(worker=False)
        assert person.state == 'sleeping'


if __name__ == '__main__':
    unittest.main()
