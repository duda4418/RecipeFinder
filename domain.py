# domain.py
"""Backwards-compat import shim for the old flat domain module.

The real implementation now lives under the recipefinder.domain package.
"""

from recipefinder.domain import *  # noqa: F401,F403
