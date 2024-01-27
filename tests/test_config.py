import pytest

from superstate import (
    InvalidConfig,
    StateChart,
    State,
)


def test_it_requires_minimal_state() -> None:
    class MyMachine(StateChart):
        """Machine to validate config."""

    # There must be at least two states
    with pytest.raises(InvalidConfig):
        MyMachine()

    class OtherMachine(StateChart):
        """Other machine to validate config."""

        __state__ = {'states': [State('open')]}

    # There must be at least two states
    with pytest.raises(InvalidConfig):
        OtherMachine()


def test_it_requires_an_initial() -> None:
    class MyMachine(StateChart):
        """Machine to validate config."""

        __state__ = {'states': [State('open'), State('closed')]}

    # There must be at least two states
    with pytest.raises(InvalidConfig):
        MyMachine()

    class AnotherMachine(StateChart):
        """Another machine to validate config."""

        __state__ = {
            'initial': None,
            'states': [State('open'), State('closed')],
        }

    # An initial state must exist.
    with pytest.raises(InvalidConfig):
        AnotherMachine()
