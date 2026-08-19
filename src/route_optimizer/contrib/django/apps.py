from django.apps import AppConfig

from route_optimizer.contrib.django import enablement, readiness


class RouteOptimizerConfig(AppConfig):
    # ``label`` is explicit: the default would be "django", which collides with every
    # django.contrib.* app label.
    name = "route_optimizer.contrib.django"
    label = "route_optimizer"
    verbose_name = "Route Optimizer"

    def ready(self) -> None:
        if not enablement.is_enabled():
            return
        readiness.connect()
