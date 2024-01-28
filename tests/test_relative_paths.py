"""Test that various paths can be used to access resources."""


def test_fully_qualified_paths(fan) -> None:
    """Test that statepaths can be referenced using full address path."""
    assert fan.state == 'off'
    assert fan.get_state('motor') == 'motor'
    assert fan.get_state('motor.off') == 'off'
    assert fan.get_state('motor.on') == 'on'
    assert fan.get_state('motor.on.high') == 'high'
    assert fan.get_state('motor.on.low') == 'low'


def test_relative_paths(fan) -> None:
    """Test that states can be referenced using relative address path."""
    assert fan.state == 'off'
    assert fan.get_state('.') == fan.state
    assert fan.get_state('..') == 'motor'
    assert fan.get_state('..off') == 'off'
    assert fan.get_state('..on') == 'on'
    fan.trigger('turn.on')
    assert fan.state == 'low'
    assert fan.get_state('...') == 'motor'
    assert fan.get_state('...off') == 'off'
    assert fan.get_state('...on') == 'on'


def test_trigger_fully_qualified_paths(fan) -> None:
    fan.trigger('turn.on')
    assert fan.state == 'low'
    fan.trigger('turn.up')
    assert fan.get_state('high') == fan.state
    fan.trigger('turn.down')
    assert fan.get_state('low') == fan.state
    fan.trigger('turn.off')
    assert fan.state == 'off'
