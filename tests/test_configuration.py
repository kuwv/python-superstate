import unittest

from fluidstate import (
    InvalidConfig,
    StateChart,
    State,
    states,
)


class ConfigurationValidation(unittest.TestCase):
    def test_it_requires_at_least_two_states(self):
        class MyMachine(StateChart):
            pass

        with self.assertRaises(InvalidConfig):
            MyMachine()
            # InvalidConfig, message="There must be at least two states"

        class OtherMachine(StateChart):
            states(State('open'))

        with self.assertRaises(InvalidConfig):
            OtherMachine()
            # InvalidConfig, message="There must be at least two states"

    def test_it_requires_an_initial(self):
        class MyMachine(StateChart):
            states(State('open'), State('closed'))

        with self.assertRaises(InvalidConfig):
            MyMachine()
            # InvalidConfig, message="There must be at least two states"

        class AnotherMachine(StateChart):
            states(State('open'), State('closed'))
            initial = None

        with self.assertRaises(InvalidConfig):
            AnotherMachine()
            # InvalidConfig, message="There must exist an initial state"


if __name__ == '__main__':
    unittest.main()
