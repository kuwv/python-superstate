import pytest

from superstate import GuardNotSatisfied, StateChart, create_machine

footsteps = []


class Foo:
    def bar(self):
        footsteps.append('on_exit looking')


foo = Foo()


def pre_falling_function():
    footsteps.append('pre falling')


class JumperGuy(StateChart):
    __machine__ = create_machine(
        {
            'initial': 'looking',
            'states': [
                {
                    'name': 'looking',
                    'transitions': [
                        {
                            'event': 'jump',
                            'target': 'falling',
                            'action': (
                                lambda jumper: jumper.append('action jump')
                            ),
                            'cond': (
                                lambda jumper: jumper.append('guard jump')
                                is None
                            ),
                        }
                    ],
                    'on_entry': lambda jumper: jumper.append('pre looking'),
                    'on_exit': foo.bar,
                },
                {'name': 'falling', 'on_entry': pre_falling_function},
            ],
        }
    )

    def __init__(self):
        super().__init__()

    def append(self, text):
        footsteps.append(text)


def test_every_callback_is_callable():
    """every callback can be a callable"""
    guy = JumperGuy()
    guy.jump()
    assert len(footsteps) == 5
    assert sorted(footsteps) == sorted(
        [
            'pre looking',
            'on_exit looking',
            'pre falling',
            'action jump',
            'guard jump',
        ]
    )


def test_deny_state_change_if_guard_callable_returns_false():
    class Door(StateChart):
        __machine__ = create_machine(
            {
                'initial': 'closed',
                'states': [
                    {'name': 'open'},
                    {
                        'name': 'closed',
                        'transitions': [
                            {
                                'event': 'open',
                                'target': 'open',
                                'cond': lambda d: not door.locked,
                            }
                        ],
                    },
                ],
            }
        )

        def locked(self):
            return self.locked

    door = Door()
    door.locked = True
    with pytest.raises(GuardNotSatisfied):
        door.open()
