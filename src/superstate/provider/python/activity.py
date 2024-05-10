"""Provide support for long running actions."""

# import inspect
# from typing import TYPE_CHECKING, Any, Callable, Tuple  # Union
#
# from superstate.exception import InvalidAction  # InvalidConfig
# from superstate.provider.base import ExecutorBase
#
# # from superstate.utils import lookup_subclasses
#
# if TYPE_CHECKING:
#     from superstate.machine import StateChart


class Activity:
    """Long running action."""
