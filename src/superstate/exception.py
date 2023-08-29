"""Provide superstate exceptions."""


class SuperstateException(Exception):
    """Manage general superstate exceptions."""


class InvalidConfig(SuperstateException):
    """Manage invalid superstate configuration exceptions."""


class InvalidTransition(SuperstateException):
    """Manage invalid superstate transition exceptions."""


class InvalidState(SuperstateException):
    """Manage invalid superstate state exceptions."""


class GuardNotSatisfied(SuperstateException):
    """Manage superstate guard excluded transition exceptions."""
