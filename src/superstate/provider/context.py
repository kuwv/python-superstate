"""Manage state context between transitions."""

# import datetime
# import platform
from collections import ChainMap
from typing import Any

# from superstate.model.system import (
#     HostInfo,
#     PlatformInfo,
#     SystemInfo,
#     RuntimeInfo,
#     TimeInfo,
# )


class Context(ChainMap):
    """Manage state context for shatechart."""

    separator: str = '.'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize settings store."""
        if 'separator' in kwargs:
            Context.separator = kwargs.pop('separator')

        super().__init__(*args)
        # SystemInfo(
        #     host=HostInfo(hostname=platform.node()),
        #     time=TimeInfo(
        #         initialized=datetime.datetime.now().isoformat(),
        #         timezone=str(
        #             datetime.datetime.now(datetime.timezone.utc)
        #             .astimezone()
        #             .tzinfo
        #         ),
        #     ),
        #     runtime=RuntimeInfo(
        #         implementation=platform.python_implementation(),
        #         version=platform.python_version(),
        #     ),
        #     platform=PlatformInfo(
        #         arch=platform.machine(),
        #         release=platform.release(),
        #         system=platform.system(),
        #         processor=platform.processor(),
        #     ),
        # ),
