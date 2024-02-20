"""Provide common types for statechart components."""

# from typing import (
#     TYPE_CHECKING,
#     Optional,
#     Type,
# )

from superstate.provider.base import Provider

# from superstate.exception import InvalidConfig
# from superstate.model.data import Data
# from superstate.provider.ecmascript.common import In
# from superstate.provider.ecmascript.executor import Action
# from superstate.provider.ecmascript.evaluator import Condition
# from superstate.utils import lookup_subclasses

# if TYPE_CHECKING:
#     from superstate.provider.base import ExecutorBase


class ECMAScript(Provider):
    "Data mode providing state data with scripting using ECMAScript." ""
