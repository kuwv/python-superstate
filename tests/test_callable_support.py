import pytest

from superstate import ConditionNotSatisfied, StateChart

footsteps = []


class Foo:
    def bar(self) -> None:
        footsteps.append('looking:on_exit')


foo = Foo()


def pre_falling_function() -> None:
    footsteps.append('falling:on_entry')


class JumperGuy(StateChart):
    state = {
        'initial': 'looking',
        'states': [
            {
                'name': 'looking',
                'transitions': [
                    {
                        'event': 'jump',
                        'cond': (
                            lambda jumper: jumper.append('jump:cond') is None
                        ),
                        'target': 'falling',
                        'content': [
                            lambda jumper: jumper.append('jump:action')
                        ],
                    }
                ],
                'on_entry': (lambda jumper: jumper.append('looking:on_entry')),
                'on_exit': foo.bar,
            },
            {'name': 'falling', 'on_entry': pre_falling_function},
        ],
    }

    @staticmethod
    def append(text: str) -> None:
        """Append a state machine action to test case."""
        footsteps.append(text)


def test_every_callback_is_callable() -> None:
    """every callback can be a callable"""
    guy = JumperGuy()
    assert guy.current_state == 'looking'
    guy.trigger('jump')
    assert guy.current_state == 'falling'
    assert len(footsteps) == 5
    assert footsteps == [
        'looking:on_entry',
        'jump:cond',
        'jump:action',
        'looking:on_exit',
        'falling:on_entry',
    ]


def test_deny_state_change_if_guard_callable_returns_false() -> None:
    class Door(StateChart):
        state = {
            'initial': 'closed',
            'states': [
                {'name': 'open'},
                {
                    'name': 'closed',
                    'transitions': [
                        {
                            'event': 'open',
                            'target': 'open',
                            'cond': lambda door: not door.locked,
                        }
                    ],
                },
            ],
        }

        @property
        def locked(self) -> bool:
            """Check if door is locked."""
            return self.__locked

        @locked.setter
        def locked(self, locked: bool) -> None:
            """Check if door is locked."""
            self.__locked = locked

    door = Door()
    door.locked = True
    with pytest.raises(ConditionNotSatisfied):
        door.trigger('open')
