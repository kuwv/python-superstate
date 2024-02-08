from superstate import StateChart, State, Transition


class JumperGuy(StateChart):
    state = {
        'initial': 'looking',
        'states': [
            State(
                'looking',
                transitions=[Transition(event='jump', target='falling')],
            ),
            State('falling'),
        ],
    }


def test_it_has_boolean_getters_for_the_states() -> None:
    """Test existence of boolean getters for states."""
    guy = JumperGuy()
    assert guy.current_state == 'looking'
    assert guy.current_state != 'falling'
    assert hasattr(guy, 'is_looking')
    assert guy.is_looking
    assert not guy.is_falling

    guy.trigger('jump')
    assert guy.current_state != 'looking'
    assert guy.current_state == 'falling'
    assert hasattr(guy, 'is_falling')
    assert not guy.is_looking
    assert guy.is_falling


def test_it_has_boolean_getters_for_individual_states() -> None:
    """Test existences of boolean getters for individual states."""
    guy = JumperGuy()
    guy.add_state(State('squashed'))
    assert hasattr(guy, 'is_squashed')
    assert not guy.is_squashed

    guy.add_transition(
        Transition(event='land', target='squashed'), statepath='falling'
    )

    guy.trigger('jump')
    assert guy.is_falling
    assert not guy.is_squashed

    guy.trigger('land')
    assert not guy.is_falling
    assert guy.is_squashed
