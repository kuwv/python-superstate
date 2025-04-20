"""Configure pytest for testing statecharts."""

from __future__ import annotations

from typing import Tuple

import pytest

from superstate import StateChart


class Switch(StateChart):
    """Example switch that can be toggled."""

    state = {
        'initial': 'off',
        'states': [
            {
                'name': 'off',
                'transitions': [{'event': 'toggle', 'target': 'on'}],
                'on_entry': 'increment_off',
            },
            {
                'name': 'on',
                'transitions': [{'event': 'toggle', 'target': 'off'}],
                'on_entry': 'increment_on',
            },
        ],
    }

    def __init__(self) -> None:
        """Initialize switch."""
        self.off_count = 0
        self.on_count = 0
        super().__init__()

    def increment_off(self) -> None:
        """Increment the count of 'off' being toggled."""
        self.off_count += 1

    def increment_on(self) -> None:
        """Increment the count of 'on' being toggled."""
        self.on_count += 1


@pytest.fixture
def switches() -> Tuple[Switch, Switch]:
    """Provide an example switch fixture."""
    return Switch(), Switch()


class Fan(StateChart):
    """Example fan."""

    state = {
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


@pytest.fixture
def fan() -> Fan:
    """Set test fixture to distribute a fan object for testing."""
    return Fan()
