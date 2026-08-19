"""Prepend the package's URL patterns to the project's root URLConf.

Done at first-request time rather than in ``AppConfig.ready()``: importing the root
URLConf during app loading is what Django warns against (circular imports, premature
translation activation). ``django.core.signals.request_started`` fires before the handler
resolves the path, so patterns inserted here — followed by ``clear_url_caches()`` —
already apply to the very request that triggered the insertion.
"""

from __future__ import annotations

import threading
from importlib import import_module
from types import ModuleType

INSTALL_FLAG = "_route_optimizer_patterns_installed"
INSTALL_ENTRY = "_route_optimizer_patterns_entry"

_lock = threading.Lock()


def _root_urlconf_module() -> ModuleType:
    from django.conf import settings

    urlconf = settings.ROOT_URLCONF
    return import_module(urlconf) if isinstance(urlconf, str) else urlconf


def prepend_urls() -> int:
    """Insert the package patterns at the top of the root URLConf.

    Returns how many patterns were inserted; 0 when they are already installed.
    """
    from django.urls import clear_url_caches, include, path

    from route_optimizer.contrib.django import urls as package_urls

    with _lock:
        root = _root_urlconf_module()
        if getattr(root, INSTALL_FLAG, False):
            return 0
        from route_optimizer.contrib.django import analyzer

        patterns = [*package_urls.urlpatterns, *analyzer.urlpatterns]
        entry = path("", include((patterns, package_urls.app_name)))
        # Rebind instead of mutating in place: ROOT_URLCONF may expose a tuple.
        root.urlpatterns = [entry, *getattr(root, "urlpatterns", [])]
        setattr(root, INSTALL_FLAG, True)
        setattr(root, INSTALL_ENTRY, entry)
        clear_url_caches()
        return len(patterns)


def reset() -> None:
    """Remove the package patterns from the root URLConf. For tests only."""
    from django.urls import clear_url_caches

    with _lock:
        root = _root_urlconf_module()
        if not getattr(root, INSTALL_FLAG, False):
            return

        ours = getattr(root, INSTALL_ENTRY, None)
        root.urlpatterns = [entry for entry in root.urlpatterns if entry is not ours]
        delattr(root, INSTALL_FLAG)
        if hasattr(root, INSTALL_ENTRY):
            delattr(root, INSTALL_ENTRY)
        clear_url_caches()
