"""Provide statechart settings for superstate."""

import datetime
import platform
from typing import Any, Dict

from superstate.config.system import (
    HostInfo,
    PlatformInfo,
    SystemInfo,
    RuntimeInfo,
    TimeInfo,
)

DEFAULT_BINDING = 'early'
DEFAULT_PROVIDER = 'default'
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

LOGGING_LEVEL = 'WARNING'
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': (
                '%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s'
            ),
            'datefmt': '%Y-%m-%dT%H:%M:%S%z',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stdout',
        }
        # 'file': {
        #     'level': 'DEBUG',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'formatter': 'default',
        #     'filename': LOGGING_FILEPATH,
        #     'maxBytes': 10485760,
        #     'backupCount': 5,
        # },
    },
    'loggers': {
        '': {
            'level': LOGGING_LEVEL,
            'handlers': [
                'console',
                # 'file',
            ],
            # 'propagate': True,
        },
    },
}
