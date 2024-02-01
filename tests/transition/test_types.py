"""Test state types and respective transitions."""

import pytest

from superstate import InvalidTransition, StateChart


class Machine(StateChart):
    """Provide example statechart."""

    __state__ = {
        'name': 'engine',
        'initial': 'stopped',
        'states': [
            {
                'name': 'started',
                'transitions': [
                    {'event': 'restart', 'target': 'started'},
                    {'event': 'stop', 'target': 'stopped'},
                ],
            },
            {'name': 'stopped', 'type': 'final'},
        ],
        'transitions': [
            {
                'event': '',
                'target': 'started',
                'cond': lambda ctx: ctx.autostart,
            }
        ],
    }

    def __init__(self, autostart: bool = False) -> None:
        self.autostart = autostart
        super().__init__()


# XXX: does not work with conditional tranient states
# def test_initial_state() -> None:
#     """Test auto-trigger."""
#     machine = Machine()
#     assert machine.initial == 'stopped'
#     assert machine.state == 'stopped'


def test_auto_trigger() -> None:
    """Test auto-trigger."""
    machine = Machine(autostart=True)
    assert machine.initial == 'stopped'
    assert machine.state == 'started'


def test_self_trigger() -> None:
    """Test self trigger."""
    machine = Machine(autostart=True)
    # assert machine.state == 'started'
    machine.trigger('restart')
    assert machine.state == 'started'


def test_final_trigger() -> None:
    """Test final trigger."""
    machine = Machine(autostart=True)
    assert machine.state == 'started'
    machine.trigger('stop')
    assert machine.state.type == 'final'
    with pytest.raises(InvalidTransition):
        machine.trigger('sabotage')
