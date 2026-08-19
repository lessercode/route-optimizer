"""Announce readiness once the Django URLConf is fully populated.

Django loads ``ROOT_URLCONF`` lazily: at ``AppConfig.ready()`` time no route exists yet,
and importing the URLConf there is discouraged (circular imports, premature translation
activation). So instead of forcing it, this module waits for the first request — the
moment the resolver is guaranteed to be populated — reports the route count, and
disconnects itself.
"""

from __future__ import annotations

import threading
from collections.abc import Iterator
from typing import IO

DISPATCH_UID = "route_optimizer.contrib.django.readiness"

_lock = threading.Lock()
_announced = False


def iter_url_patterns(resolver) -> Iterator[object]:
    """Yield every leaf URLPattern under ``resolver``, descending into included URLConfs."""
    for entry in resolver.url_patterns:
        if hasattr(entry, "url_patterns"):
            yield from iter_url_patterns(entry)
        else:
            yield entry


def count_routes(resolver=None) -> int:
    """Number of concrete routes reachable from ``resolver`` (defaults to ROOT_URLCONF)."""
    from django.urls import get_resolver

    if resolver is None:
        resolver = get_resolver()
    return sum(1 for _ in iter_url_patterns(resolver))


def announce_ready(*, stream: IO[str] | None = None) -> bool:
    global _announced

    with _lock:
        if _announced:
            return False
        _announced = True
    return True


def _on_first_request(sender, **kwargs) -> None:
    from django.core.signals import request_started

    from route_optimizer.contrib.django import urlconf

    request_started.disconnect(dispatch_uid=DISPATCH_UID)
    urlconf.prepend_urls()
    announce_ready()


def connect() -> None:
    """Arm the one-shot receiver. Idempotent thanks to ``dispatch_uid``."""
    from django.core.signals import request_started

    request_started.connect(_on_first_request, dispatch_uid=DISPATCH_UID, weak=False)


def reset() -> None:
    """Forget that readiness was announced. For tests only."""
    global _announced

    with _lock:
        _announced = False
