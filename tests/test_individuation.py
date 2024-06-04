"""Test that instances maintain individuation."""

from superstate import State, StateChart, Transition


class Door(StateChart):
    """Provide door example for testing."""

    state = {
        'initial': 'closed',
        'states': [
            {
                'name': 'closed',
                'transitions': [{'event': 'open', 'target': 'opened'}],
            },
            {'name': 'opened'},
        ],
    }


door = Door()
door.add_state(State(name='broken'))
door.add_transition(
    Transition(event='crack', target='broken'), statepath='closed'
)


def test_it_responds_to_an_event() -> None:
    """Test door responds to an event."""
    assert hasattr(door.current_state, 'crack')


def test_event_changes_state_when_called() -> None:
    """Test event changes state when called."""
    door.trigger('crack')
    assert door.current_state == 'broken'


def test_it_informs_all_its_states() -> None:
    """Test machine informs all states."""
    assert len(door.states) == 3
    assert door.states == ('closed', 'opened', 'broken')


def test_individuation_does_not_affect_other_instances() -> None:
    """Test individuation does not affect other instances."""
    another_door = Door()
    assert not hasattr(another_door.current_state, 'crack')
