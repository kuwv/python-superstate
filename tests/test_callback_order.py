import pytest

from superstate import StateChart


class CrazyGuy(StateChart):
    __datamodel__ = 'python'
    __state__ = {
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
                'on_exit': 'no_looking_anymore',
            },
            {'name': 'falling', 'on_entry': 'will_fall_right_now'},
        ],
    }

    def __init__(self):
        super().__init__()
        self.at_risk = False
        self.callbacks = []

    def become_at_risk(self):
        self.at_risk = True
        self.callbacks.append('action')

    def no_looking_anymore(self):
        self.callbacks.append('on_exit')

    def will_fall_right_now(self):
        self.callbacks.append('on_entry')

    def always_can_jump(self):
        self.callbacks.append('guard')
        return True


@pytest.fixture
def setup_guy():
    guy = CrazyGuy()
    guy.trigger('jump')
    return guy


def test_it_runs_guard_first(setup_guy):
    """(1) guard"""
    assert setup_guy.callbacks[0] == 'guard'


def test_it_and_then_transaction_action(setup_guy):
    """(4) transaction action"""
    assert setup_guy.callbacks[1] == 'action'


def test_it_and_then_old_state_on_exit(setup_guy):
    """(2) old state on_exit action"""
    assert setup_guy.callbacks[2] == 'on_exit'


def test_it_and_then_new_state_on_exit(setup_guy):
    """(3) new state pre action"""
    assert setup_guy.callbacks[3] == 'on_entry'
