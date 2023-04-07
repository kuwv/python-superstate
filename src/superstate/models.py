"""Provide common types for statechart components."""

from typing import Optional

from superstate.exception import InvalidConfig


class NameDescriptor:
    """Validate state naming."""

    __slots__ = ['name']

    def __set_name__(self, owner: object, name: str) -> None:
        self.name = name  # pylint: disable=attribute-defined-outside-init

    def __get__(self, obj: object, objtype: Optional[str] = None) -> str:
        return getattr(obj, self.name)

    def __set__(self, obj: object, value: str) -> None:
        if not value.replace('_', '').isalnum():
            raise InvalidConfig('state name contains invalid characters')
        setattr(obj, self.name, value)
