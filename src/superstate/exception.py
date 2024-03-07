"""Provide superstate exception."""


class SuperstateException(Exception):
    """Manage general superstate exception."""


class InvalidAction(SuperstateException):
    """Manage invalid superstate action exception."""


class InvalidConfig(SuperstateException):
    """Manage invalid superstate configuration exception."""


class InvalidPath(SuperstateException):
    """Manage invalid superstate path exception."""


class InvalidTransition(SuperstateException):
    """Manage invalid superstate transition exception."""


class InvalidState(SuperstateException):
    """Manage invalid superstate state exception."""


class ConditionNotSatisfied(SuperstateException):
    """Manage superstate guard excluded transition exception."""
