# Copyright (c) 2022 Jesse P. Johnson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Robust statechart for configurable automation rules."""

import logging
from typing import Any, Dict, List, Union

from superstate.exception import (
    InvalidConfig,
    InvalidState,
    InvalidTransition,
    ForkedTransition,
    GuardNotSatisfied,
)
from superstate.machine import StateChart
from superstate.state import CompositeState, State
from superstate.transition import Transition

__author__ = 'Jesse P. Johnson'
__author_email__ = 'jpj6652@gmail.com'
__title__ = 'superstate'
__description__ = 'Compact statechart that can be vendored.'
__version__ = '1.1.0a3'
__license__ = 'MIT'
__copyright__ = 'Copyright 2022 Jesse Johnson.'
__all__ = (
    'StateChart',
    'states',
    'state',
    'transitions',
    'transition',
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def transition(config: Union['Transition', dict]) -> 'Transition':
    """Create transition from configuration."""
    if isinstance(config, Transition):
        return config
    if isinstance(config, dict):
        return Transition(
            event=config['event'],
            target=config['target'],
            action=config.get('action'),
            cond=config.get('cond'),
        )
    raise InvalidConfig('could not find a valid transition configuration')


def transitions(*args: Any) -> List['Transition']:
    """Create transitions from configuration."""
    return list(map(transition, args))


def state(
    config: Union['State', dict, str]
) -> Union['CompositeState', 'State']:
    """Create state from configuration."""
    if isinstance(config, State):
        return config
    if isinstance(config, str):
        # pylint: disable-next=abstract-class-instantiated
        return State(config)  # type: ignore
    if isinstance(config, dict):
        cls = config.pop('factory', State)
        return cls(
            name=config.get('name', 'superstate'),
            initial=config.get('initial'),
            kind=config.get('kind'),
            states=(states(*config['states']) if 'states' in config else []),
            transitions=(
                transitions(*config['transitions'])
                if 'transitions' in config
                else []
            ),
            on_entry=config.get('on_entry'),
            on_exit=config.get('on_exit'),
        )
    raise InvalidConfig('could not find a valid state configuration')


# def states(*args: Any) -> List['State']:
def states(*args: Any) -> List['State']:
    """Create states from configuration."""
    return list(map(state, args))
