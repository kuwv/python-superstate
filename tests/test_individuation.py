"""Superstate object (individuation)"""

from superstate import StateChart, State, Transition, state


class Door(StateChart):
    """Provide door example for testing."""

    __superstate__ = state(
        {
            'initial': 'closed',
            'states': [
                {
                    'name': 'closed',
                    'transitions': [{'event': 'open', 'target': 'opened'}],
                },
                {'name': 'opened'},
            ],
        }
    )


door = Door()
door.add_state(State(name='broken'))
door.add_transition(
    Transition(event='crack', target='broken'), statepath='closed'
)


def test_it_responds_to_an_event():
    """Test door responds to an event."""
    assert hasattr(door.state, 'crack')


def test_event_changes_state_when_called():
    """Test event changes state when called."""
    door.crack()
    assert door.state == 'broken'


def test_it_informs_all_its_states():
    """Test machine informs all states."""
    assert len(door.states) == 3
    assert door.states == ('closed', 'opened', 'broken')


def test_individuation_does_not_affect_other_instances():
    """Test individuation does not affect other instances."""
    another_door = Door()
    assert not hasattr(another_door.state, 'crack')
