from fluidstate import StateChart, State, Transition, states


class JumperGuy(StateChart):
    states(
        State('looking', [Transition(event='jump', target='falling')]),
        State('falling'),
    )
    initial = 'looking'


def test_it_has_boolean_getters_for_the_states():
    guy = JumperGuy()
    assert hasattr(guy, 'is_looking')
    assert hasattr(guy, 'is_falling')
    assert guy.state == 'looking'
    assert guy.state != 'falling'

    guy.jump()
    assert guy.state != 'looking'
    assert guy.state == 'falling'


def test_it_has_boolean_getters_for_individual_states():
    guy = JumperGuy()
    guy.add_state(State('squashed'))
    assert hasattr(guy, 'is_squashed')
    assert guy.state != 'squashed'

    guy.add_transition(
        Transition(event='land', target='squashed'), state='falling'
    )
    guy.jump()
    guy.land()
    assert guy.state == 'squashed'
