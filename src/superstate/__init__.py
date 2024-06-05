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
import logging.config

# from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union

from superstate.config import LOGGING_CONFIG
from superstate.exception import (
    InvalidConfig,
    InvalidState,
    InvalidTransition,
    ConditionNotSatisfied,
)
from superstate.provider import Provider
from superstate.machine import StateChart
from superstate.model import (
    Action,
    Assign,
    Data,
    DataModel,
    DoneData,
    If,
    ElseIf,
    Else,
    ForEach,
    Log,
    Raise,
    Script,
)
from superstate.state import (
    AtomicState,
    CompositeState,
    CompoundState,
    ConditionState,
    FinalState,
    # HistoryState,
    State,
    ParallelState,
    PseudoState,
)
from superstate.transition import Transition

__author__ = 'Jesse P. Johnson'
__author_email__ = 'jpj6652@gmail.com'
__title__ = 'superstate'
__description__ = 'Compact statechart that can be vendored.'
__version__ = '1.6.1a1'
__license__ = 'MIT'
__copyright__ = 'Copyright 2022 Jesse Johnson.'
__all__ = (
    'StateChart',
    # states
    'AtomicState',
    'CompositeState',
    'CompoundState',
    'ConditionState',
    'FinalState',
    # 'HistoryState',
    'State',
    'ParallelState',
    'PseudoState',
    # Exceptions
    'InvalidConfig',
    'InvalidState',
    'InvalidTransition',
    'ConditionNotSatisfied',
    # DataModel
    'Assign',
    'Data',
    'DataModel',
    'DoneData',
    'If',
    'ElseIf',
    'Else',
    'ForEach',
    'Log',
    'Raise',
    'Script',
)

logging.config.dictConfig(LOGGING_CONFIG)
logging.getLogger(__name__).addHandler(logging.NullHandler())
