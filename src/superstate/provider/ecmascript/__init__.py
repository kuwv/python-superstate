"""Provide common types for statechart components."""

from dataclasses import dataclass

# from typing import (
#     TYPE_CHECKING,
#     Optional,
#     Type,
# )

from superstate.provider.base import DataModel

# from superstate.exception import InvalidConfig
# from superstate.model.data import Data
# from superstate.provider.ecmascript.common import In
# from superstate.provider.ecmascript.executor import Action
# from superstate.provider.ecmascript.evaluator import Condition
# from superstate.utils import lookup_subclasses

# if TYPE_CHECKING:
#     from superstate.model.expression.base import ActionBase, ConditionBase


@dataclass
class ECMAScript(DataModel):
    "Data mode providing state data with scripting using ECMAScript." ""
