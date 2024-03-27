"""Provide system info for statechart components."""

from typing import NotRequired, TypedDict


class HostInfo(TypedDict):
    """Provide settings for host info."""

    hostname: str
    url: NotRequired[str]


class PlatformInfo(TypedDict):
    """Provide settings for platform settings."""

    arch: str
    release: str
    system: str
    processor: str


class RuntimeInfo(TypedDict):
    """Provide settings for python info."""

    implementation: str
    version: str


class TimeInfo(TypedDict):
    """Provide settings for timezone info."""

    initialized: str
    timezone: str
    # offset: str


class SystemInfo(TypedDict):
    """Provide system info."""

    host: NotRequired['HostInfo']
    time: NotRequired['TimeInfo']
    runtime: NotRequired['RuntimeInfo']
    platform: NotRequired['PlatformInfo']
