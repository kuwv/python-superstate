from superstate import StateChart, State, Transition, state


class JumperGuy(StateChart):
    __superstate__ = state(
        {
            'initial': 'looking',
            'states': [
                State(
                    'looking',
                    transitions=[Transition(event='jump', target='falling')],
                ),
                State('falling'),
            ],
        }
    )


def test_it_has_boolean_getters_for_the_states():
    guy = JumperGuy()
    assert hasattr(guy, 'is_looking')
    assert hasattr(guy, 'is_falling')
    assert guy.state == 'looking'
    assert guy.state != 'falling'

    guy.trigger('jump')
    assert guy.state != 'looking'
    assert guy.state == 'falling'


def test_it_has_boolean_getters_for_individual_states():
    guy = JumperGuy()
    guy.add_state(State('squashed'))
    assert hasattr(guy, 'is_squashed')
    assert guy.state != 'squashed'

    guy.add_transition(
        Transition(event='land', target='squashed'), statepath='falling'
    )
    guy.trigger('jump')
    guy.trigger('land')
    assert guy.state == 'squashed'
