import pytest

from superstate import StateChart, state


class SwitchMachine(StateChart):
    __superstate__ = state(
        {
            'initial': 'off',
            'states': [
                {
                    'name': 'off',
                    'transitions': [{'event': 'toggle', 'target': 'on'}],
                    'on_entry': 'inc_off',
                },
                {
                    'name': 'on',
                    'transitions': [{'event': 'toggle', 'target': 'off'}],
                    'on_entry': 'inc_on',
                },
            ],
        }
    )

    def __init__(self):
        self.off_count = 0
        self.on_count = 0
        super().__init__()

    def inc_off(self):
        self.off_count += 1

    def inc_on(self):
        self.on_count += 1


@pytest.fixture
def switch_machine():
    machine = SwitchMachine()
    return machine


class FallingMachine(StateChart):
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
                            'cond': ['ready_to_fly', 'high_enough'],
                        }
                    ],
                },
                {'name': 'falling'},
            ],
        }
    )

    def __init__(self, ready=True):
        super().__init__()
        self.ready = ready
        self.high_enough_flag = True

    def ready_to_fly(self):
        return self.ready

    def high_enough(self):
        return self.high_enough_flag


@pytest.fixture
def machine():
    f = FallingMachine()
    return f
