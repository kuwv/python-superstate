"""Test state independence."""


def test_two_switchs_do_not_share_transitions(switches) -> None:
    switch_a, switch_b = switches

    assert switch_a.current_state == 'off'
    assert switch_b.current_state == 'off'

    switch_a.trigger('toggle')

    assert switch_a.current_state == 'on'
    assert switch_b.current_state == 'off'


def test_two_switchs_do_not_share_actions(switches) -> None:
    """Test the indepedence between two statecharts."""
    switch_a, switch_b = switches

    assert switch_a.on_count == 0
    assert switch_b.on_count == 0

    switch_a.trigger('toggle')

    assert switch_a.on_count == 1
    assert switch_b.on_count == 0
