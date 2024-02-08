"""Provide statechart settings for superstate."""

import datetime
import platform
from typing import Any, Dict

from superstate.model.system import (
    HostInfo,
    PlatformInfo,
    SystemInfo,
    RuntimeInfo,
    TimeInfo,
)

DEFAULT_BINDING: str = 'early'

DEFAULT_DATAMODEL: Dict[str, Any] = {
    'systeminfo': SystemInfo(
        host=HostInfo(hostname=platform.node()),
        time=TimeInfo(
            initialized=datetime.datetime.now().isoformat(),
            timezone=str(
                datetime.datetime.now(datetime.timezone.utc)
                .astimezone()
                .tzinfo
            ),
        ),
        runtime=RuntimeInfo(
            implementation=platform.python_implementation(),
            version=platform.python_version(),
        ),
        platform=PlatformInfo(
            arch=platform.machine(),
            release=platform.release(),
            system=platform.system(),
            processor=platform.processor(),
        ),
    )
}
