import pytest

from superstate import (
    InvalidConfig,
    StateChart,
    State,
    create_machine,
)


def test_it_requires_at_least_two_states():
    class MyMachine(StateChart):
        pass

    # There must be at least two states
    with pytest.raises(InvalidConfig):
        MyMachine()

    class OtherMachine(StateChart):
        __machine__ = create_machine({'states': [State('open')]})

    # There must be at least two states
    with pytest.raises(InvalidConfig):
        OtherMachine()


def test_it_requires_an_initial():
    class MyMachine(StateChart):
        __machine__ = create_machine(
            {'states': [State('open'), State('closed')]}
        )

    # There must be at least two states
    with pytest.raises(InvalidConfig):
        MyMachine()

    class AnotherMachine(StateChart):
        __machine__ = create_machine(
            {
                'initial': None,
                'states': [State('open'), State('closed')],
            }
        )

    # An initial state must exist.
    with pytest.raises(InvalidConfig):
        AnotherMachine()
