import unittest

from fluidstate import StateMachine, state, transition
from fluidstate import FluidstateNeedNotSatisfied


class FallingMachine(StateMachine):
    state('looking')
    state('falling')
    initial_state = 'looking'
    transition(
        source='looking',
        event='jump',
        target='falling',
        need=['ready_to_fly', 'high_enough'],
    )

    def __init__(self, ready=True):
        StateMachine.__init__(self)
        self.ready = ready
        self.high_enough_flag = True

    def ready_to_fly(self):
        return self.ready

    def high_enough(self):
        return self.high_enough_flag


class FluidstateNeed(unittest.TestCase):
    def test_it_allows_transition_if_satisfied(self):
        machine = FallingMachine()
        try:
            machine.jump()
        except Exception:
            self.fail('machine failed to jump')
        assert machine.current_state == 'falling'

    def test_it_forbids_transition_if_not_satisfied(self):
        machine = FallingMachine(ready=False)
        with self.assertRaises(FluidstateNeedNotSatisfied):
            machine.jump()

    def test_it_may_be_an_attribute(self):
        """it may be an attribute, not only a method"""
        machine = FallingMachine()
        machine.ready_to_fly = False
        with self.assertRaises(FluidstateNeedNotSatisfied):
            machine.jump()

        machine.ready_to_fly = True
        try:
            machine.jump()
        except Exception:
            self.fail('machine jump failed')
        assert machine.current_state == 'falling'

    def test_it_allows_transition_only_if_all_are_satisfied(self):
        machine = FallingMachine()
        machine.ready_to_fly = True
        machine.high_enough_flag = True
        try:
            machine.jump()
        except Exception:
            self.fail('machine failed to jump')

        machine = FallingMachine()
        machine.ready_to_fly = False
        machine.high_enough_flag = True
        with self.assertRaises(FluidstateNeedNotSatisfied):
            machine.jump()

        machine = FallingMachine()
        machine.ready_to_fly = True
        machine.high_enough_flag = False
        with self.assertRaises(FluidstateNeedNotSatisfied):
            machine.jump()


if __name__ == '__main__':
    unittest.main()
