# route-optimizer

Django URL pattern optimization.

Current state: the package prepends its own URL patterns to the project's root URLConf and
prints a readiness line once every route is resolved. The optimization itself is not
implemented yet.

## Install

```bash
pip install route-optimizer[django]
```

## Usage

Add the integration to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...,
    "route_optimizer.contrib.django",
]
```

Django has resolved every route by the time the first request arrives. At that point the
package prepends its own patterns to the root URLConf, so they win over project routes
with the same path, and prints:

```
route-optimizer: ready (12 routes)
```

The injection applies to that very first request: `GET /__route_optimizer__/` answers even
when it *is* the first request.

Nothing is imported from the root URLConf at `AppConfig.ready()` time, since Django warns
against that (circular imports, premature translation activation). The work hangs off
`django.core.signals.request_started`, which fires before the handler resolves the path.

## Dev mode

On a local run the integration stays off, since it has nothing useful to do there. A run
counts as local when `DEBUG` is on **or** the process was started with `runserver`. To turn
it on anyway, set the environment variable:

```bash
ROUTE_OPTIMIZER_DEV_MODE=1
```

Accepted truthy values: `1`, `true`, `yes`, `on`. Anything else (including an unset
variable) leaves the integration disabled on local runs. Off a local run it is always
active.

## Layout

```
src/route_optimizer/
└── contrib/django/
    ├── apps.py          # AppConfig, arms the hook when enabled
    ├── enablement.py    # dev-mode gate
    ├── readiness.py     # one-shot request_started hook
    ├── urlconf.py       # prepends package patterns to ROOT_URLCONF
    ├── urls.py          # the package's own patterns
    └── views.py
```

## Development

```bash
uv sync --extra django --extra dev
source .venv/bin/activate
ruff check .
```
