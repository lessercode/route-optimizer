"""URL patterns owned by the package.

These are prepended to the project's root URLConf, so they win over any project route
matching the same path. The prefix is deliberately unlikely to collide.
"""

from django.urls import path

from route_optimizer.contrib.django import views

app_name = "route_optimizer"

urlpatterns = [
    path("__route_optimizer__/", views.status, name="status"),
]
