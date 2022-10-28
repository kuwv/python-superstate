import unittest

from fluidstate import StateChart, State, Transition, states


class Door(StateChart):
    states(
        State(
            'closed',
            [Transition(event='open', target='open')],
        ),
        State('open'),
    )
    initial = 'closed'


class IndividuationSpec(unittest.TestCase):
    """Fluidstate object (individuation)"""

    def setUp(self):
        self.door = Door()
        self.door.add_state(State('broken'))
        self.door.add_transition(
            Transition(event='crack', target='broken'),
            state='closed',
        )

    def test_it_responds_to_an_event(self):
        assert hasattr(self.door, 'crack')

    def test_event_changes_state_when_called(self):
        self.door.crack()
        assert self.door.state == 'broken'

    def test_it_informs_all_its_states(self):
        assert len(self.door.states) == 3
        assert self.door.states == ['closed', 'open', 'broken']

    # XXX: this has been converted to __getattr__ instead
    # def test_individuation_does_not_affect_other_instances(self):
    #     another_door = Door()
    #     assert not hasattr(another_door, 'crack')


if __name__ == '__main__':
    unittest.main()
