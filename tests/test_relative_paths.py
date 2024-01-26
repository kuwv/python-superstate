"""Provide example meta-state."""

from superstate import StateChart


class Fan(StateChart):
    """Example fan."""

    __state__ = {
        'name': 'motor',
        'initial': 'off',
        'states': [
            {
                'name': 'off',
                'transitions': [{'event': 'turn.on', 'target': 'on'}],
            },
            {
                'name': 'on',
                'initial': 'low',
                'states': [
                    {
                        'name': 'low',
                        'transitions': [
                            {'event': 'turn.up', 'target': 'high'},
                        ],
                    },
                    {
                        'name': 'high',
                        'transitions': [
                            {'event': 'turn.down', 'target': 'low'},
                        ],
                    },
                ],
                'transitions': [{'event': 'turn.off', 'target': 'off'}],
            },
        ],
    }


def test_fully_qualified_paths():
    fan = Fan()
    assert fan.state == 'off'
    assert fan.get_state('motor') == 'motor'
    assert fan.get_state('motor.off') == 'off'
    assert fan.get_state('motor.on') == 'on'
    assert fan.get_state('motor.on.high') == 'high'
    assert fan.get_state('motor.on.low') == 'low'


def test_relative_paths():
    fan = Fan()
    assert fan.state == 'off'
    assert fan.get_state('.') == fan.state
    assert fan.get_state('..') == 'motor'
    assert fan.get_state('..off') == 'off'
    assert fan.get_state('..on') == 'on'


def test_transition_of_relative_state_target():
    fan = Fan()
    fan.trigger('turn.on')
    assert fan.state == 'low'
    assert fan.get_state('...') == 'motor'
    assert fan.get_state('...off') == 'off'
    assert fan.get_state('...on') == 'on'


def test_nested_relative_paths():
    fan = Fan()
    fan.trigger('turn.on')
    assert fan.state == 'low'
    fan.trigger('turn.up')
    assert fan.get_state('high') == fan.state
    fan.trigger('turn.down')
    assert fan.get_state('low') == fan.state
    fan.trigger('turn.off')
    assert fan.state == 'off'
