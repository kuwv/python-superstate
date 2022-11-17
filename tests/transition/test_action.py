from superstate import StateChart, create_machine


class CrazyGuy(StateChart):
    create_machine(
        {
            'initial': 'looking',
            'states': [
                {
                    'name': 'looking',
                    'transitions': [
                        {
                            'event': 'jump',
                            'target': 'falling',
                            'action': ['become_at_risk', 'accelerate'],
                        }
                    ],
                },
                {'name': 'falling'},
            ],
        }
    )

    def __init__(self):
        super().__init__()
        self.at_risk = False
        self.accelerating = False

    def become_at_risk(self):
        self.at_risk = True

    def accelerate(self):
        self.accelerating = True


def test_it_runs_when_transition_occurs():
    guy = CrazyGuy()
    assert guy.at_risk is False

    guy.jump()
    assert guy.at_risk is True


def test_it_supports_multiple_transition_actions():
    guy = CrazyGuy()
    assert guy.at_risk is False
    assert guy.accelerating is False

    guy.jump()
    assert guy.at_risk is True
    assert guy.accelerating is True
