from superstate import StateChart


class CrazyGuy(StateChart):
    state = {
        'initial': 'looking',
        'states': [
            {
                'name': 'looking',
                'transitions': [
                    {
                        'event': 'jump',
                        'target': 'falling',
                        'content': ['become_at_risk', 'accelerate'],
                    }
                ],
            },
            {'name': 'falling'},
        ],
    }

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

    guy.trigger('jump')
    assert guy.at_risk is True


def test_it_supports_multiple_transition_content():
    guy = CrazyGuy()
    assert guy.at_risk is False
    assert guy.accelerating is False

    guy.trigger('jump')
    assert guy.at_risk is True
    assert guy.accelerating is True
