import pytest

from superstate import GuardNotSatisfied, StateChart, state

footsteps = []


class Foo:
    def bar(self):
        footsteps.append('looking:on_exit')


foo = Foo()


def pre_falling_function():
    footsteps.append('falling:on_entry')


class JumperGuy(StateChart):
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
                            'action': (
                                lambda jumper: jumper.append('looking:action')
                            ),
                            'cond': (
                                lambda jumper: jumper.append('looking:cond')
                                is None
                            ),
                        }
                    ],
                    'on_entry': (
                        lambda jumper: jumper.append('looking:on_entry')
                    ),
                    'on_exit': foo.bar,
                },
                {'name': 'falling', 'on_entry': pre_falling_function},
            ],
        }
    )

    @staticmethod
    def append(text):
        footsteps.append(text)


def test_every_callback_is_callable():
    """every callback can be a callable"""
    guy = JumperGuy()
    assert guy.state == 'looking'
    guy.trigger('jump')
    assert guy.state == 'falling'
    assert len(footsteps) == 5
    assert sorted(footsteps) == sorted(
        [
            'looking:cond',
            'looking:on_entry',
            'looking:action',
            'looking:on_exit',
            'falling:on_entry',
        ]
    )


def test_deny_state_change_if_guard_callable_returns_false():
    class Door(StateChart):
        __superstate__ = state(
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
