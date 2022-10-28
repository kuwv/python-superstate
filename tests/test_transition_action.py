import unittest

from fluidstate import StateChart, State, Transition, states, transitions


class CrazyGuy(StateChart):
    states(
        State(
            'looking',
            transitions(
                Transition(
                    event='jump',
                    target='falling',
                    action=['become_at_risk', 'accelerate'],
                )
            ),
        ),
        State('falling'),
    )
    initial = 'looking'

    def __init__(self):
        StateChart.__init__(self)
        self.at_risk = False
        self.accelerating = False

    def become_at_risk(self):
        self.at_risk = True

    def accelerate(self):
        self.accelerating = True


class FluidstateTransitionAction(unittest.TestCase):
    def test_it_runs_when_transition_occurs(self):
        guy = CrazyGuy()
        assert guy.at_risk is False

        guy.jump()
        assert guy.at_risk is True

    def test_it_supports_multiple_transition_actions(self):
        guy = CrazyGuy()
        assert guy.at_risk is False
        assert guy.accelerating is False

        guy.jump()
        assert guy.at_risk is True
        assert guy.accelerating is True


if __name__ == '__main__':
    unittest.main()
