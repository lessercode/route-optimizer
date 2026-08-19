"""Decide whether the integration should run at all.

On a developer machine the package has nothing useful to do, so it stays out of the way:
when the project looks local (``DEBUG`` on, or the process was started with ``runserver``)
it only activates if dev mode is explicitly switched on through the environment.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Sequence

ENV_VAR = "ROUTE_OPTIMIZER_DEV_MODE"
_TRUTHY = frozenset({"1", "true", "yes", "on"})
LOCAL_COMMANDS = frozenset({"runserver"})


def dev_mode() -> bool:
    """True when ``ROUTE_OPTIMIZER_DEV_MODE`` is set to a truthy value."""
    return os.environ.get(ENV_VAR, "").strip().lower() in _TRUTHY


def is_local_environment(argv: Sequence[str] | None = None) -> bool:
    """True when the project looks like a local/dev run."""
    from django.conf import settings

    if getattr(settings, "DEBUG", False):
        return True
    argv = sys.argv if argv is None else argv
    return any(arg in LOCAL_COMMANDS for arg in argv[1:])


def is_enabled(argv: Sequence[str] | None = None) -> bool:
    """The integration runs everywhere except local runs without dev mode."""
    return dev_mode() or not is_local_environment(argv)
