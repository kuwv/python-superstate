import unittest

from fluidstate import (
    # InvalidTransition
    StateChart,
    state,
    transition,
)


class MyMachine(StateChart):

    initial = 'off'

    state('off', on_entry='inc_off')
    state('on', on_entry='inc_on')

    transition(event='toggle', target='on')
    transition(event='toggle', target='off')

    def __init__(self):
        self.off_count = 0
        self.on_count = 0
        super(MyMachine, self).__init__()

    def inc_off(self):
        self.off_count += 1

    def inc_on(self):
        self.on_count += 1


class MachineIndependence(unittest.TestCase):
    def test_two_machines_dont_share_transitions(self):
        machine_a = MyMachine()
        machine_b = MyMachine()

        assert machine_a.state == 'off'
        assert machine_b.state == 'off'

        machine_a.toggle()

        assert machine_a.state == 'on'
        assert machine_b.state == 'off'

    def test_two_machines_dont_share_actions(self):
        machine_a = MyMachine()
        machine_b = MyMachine()

        machine_a.on_count == 0
        machine_b.on_count == 0

        machine_a.toggle()

        machine_a.on_count == 1
        machine_b.on_count == 0


if __name__ == '__main__':
    unittest.main()
