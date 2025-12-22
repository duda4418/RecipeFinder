# providers.py
"""Backwards-compat import shim for the old flat providers module.

The real implementations now live under the recipefinder.providers package.
"""

from recipefinder.providers import *  # noqa: F401,F403
