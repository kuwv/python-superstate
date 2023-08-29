"""Provide common types for statechart components."""

from typing import Optional

from superstate.exception import InvalidConfig


class NameDescriptor:
    """Validate state naming."""

    __slots__ = ['id']

    def __set_id__(self, owner: object, id: str) -> None:
        self.id = id  # pylint: disable=attribute-defined-outside-init

    def __get__(self, obj: object, objtype: Optional[str] = None) -> str:
        return getattr(obj, self.id)

    def __set__(self, obj: object, value: str) -> None:
        if not value.replace('_', '').isalnum():
            raise InvalidConfig('state id contains invalid characters')
        setattr(obj, self.id, value)
