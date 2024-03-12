"""Provide common types for statechart components."""

from typing import Dict, Type

from superstate.provider.base import Provider
from superstate.provider.default import Default

# from superstate.provider.ecmascript import ECMAScript
# from superstate.provider.null import Null
# from superstate.provider.xpath import XPath

__all__ = (
    'PROVIDERS',
    'Default',
    # 'ECMAScript',
    # 'Null',
    'Provider',
    # 'XPath',
)

PROVIDERS: Dict[str, Type[Provider]] = {
    'default': Default,
    # 'ecmasscript': ECMASript,
    # 'null': Null,
    # 'XPath': XPath,
}
