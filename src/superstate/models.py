"""Provide common types for statechart components."""

from typing import Optional

from superstate.exception import InvalidConfig


class NameDescriptor:
    """Validate state naming."""

    __slots__ = ['__name']

    def __init__(self, name: str) -> None:
        self.__name = name

    def __get__(self, key: str, objtype: Optional[str] = None) -> str:
        return getattr(key, self.__name)

    def __set__(self, key: str, value: str) -> None:
        if not value.replace('_', '').isalnum():
            raise InvalidConfig('state name contains invalid characters')
        setattr(key, self.__name, value)
