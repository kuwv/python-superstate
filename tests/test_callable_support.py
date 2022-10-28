import unittest

from fluidstate import (
    GuardNotSatisfied,
    StateChart,
    State,
    Transition,
    states,
    transitions,
)

footsteps = []


class Foo:
    def bar(self):
        footsteps.append('on_exit looking')


foo = Foo()


def pre_falling_function():
    footsteps.append('pre falling')


class JumperGuy(StateChart):
    states(
        State(
            'looking',
            transitions=transitions(
                Transition(
                    event='jump',
                    target='falling',
                    action=lambda jumper: jumper.append('action jump'),
                    cond=lambda jumper: jumper.append('guard jump') is None,
                )
            ),
            on_entry=lambda jumper: jumper.append('pre looking'),
            on_exit=foo.bar,
        ),
        State('falling', on_entry=pre_falling_function),
    )
    initial = 'looking'

    def __init__(self):
        StateChart.__init__(self)

    def append(self, text):
        footsteps.append(text)


class CallableSupport(unittest.TestCase):
    def test_every_callback_can_be_a_callable(self):
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

    def test_deny_state_change_if_guard_callable_returns_false(self):
        class Door(StateChart):
            states(
                State('open'),
                State(
                    'closed',
                    transitions(
                        Transition(
                            event='open',
                            target='open',
                            cond=lambda d: not door.locked,
                        )
                    ),
                ),
            )
            initial = 'closed'

            def locked(self):
                return self.locked

        door = Door()
        door.locked = True
        with self.assertRaises(GuardNotSatisfied):
            door.open()


if __name__ == '__main__':
    unittest.main()
