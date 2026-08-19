from django.http import HttpRequest, HttpResponse

from route_optimizer import __version__


def status(request: HttpRequest) -> HttpResponse:
    """Placeholder endpoint proving the package's own patterns are wired in."""
    return HttpResponse(f"route-optimizer {__version__}: ok")
