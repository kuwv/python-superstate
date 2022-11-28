import pytest

from superstate import StateChart, state


class CrazyGuy(StateChart):
    __superstate__ = state(
        {
            'initial': 'looking',
            'states': [
                {
                    'name': 'looking',
                    'transitions': [
                        {
                            'event': 'jump',
                            'target': 'falling',
                            'action': 'become_at_risk',
                            'cond': 'always_can_jump',
                        },
                    ],
                    'on_exit': 'no_lookin_anymore',
                },
                {'name': 'falling', 'on_entry': 'will_fall_right_now'},
            ],
        }
    )

    def __init__(self):
        super().__init__()
        self.at_risk = False
        self.callbacks = []

    def become_at_risk(self):
        self.at_risk = True
        self.callbacks.append('action')

    def no_lookin_anymore(self):
        self.callbacks.append('old on_exit')

    def will_fall_right_now(self):
        self.callbacks.append('new pre')

    def always_can_jump(self):
        self.callbacks.append('guard')
        return True


@pytest.fixture
def setup_guy():
    guy = CrazyGuy()
    guy.jump()
    return guy


def test_it_runs_guard_first(setup_guy):
    """(1) guard"""
    setup_guy.callbacks[0] == 'guard'


def test_it_and_then_old_state_on_exit(setup_guy):
    """(2) old state on_exit action"""
    setup_guy.callbacks[1] == 'old on_exit'


def test_it_and_then_new_state_on_exit(setup_guy):
    """(3) new state pre action"""
    setup_guy.callbacks[2] == 'new pre'


def test_it_and_then_transaction_action(setup_guy):
    """(4) transaction action"""
    setup_guy.callbacks[3] == 'action'
