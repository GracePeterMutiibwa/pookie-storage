# Installation

## Requirements

- Python 3.10 or higher
- Django 3.2 or higher

## Install the package

```bash
pip install pookie-storage
```

## Add to INSTALLED_APPS

```python
INSTALLED_APPS = [
    ...
    "pookieStorage",
]
```

Django uses this to run pookieStorage's startup validation. If `POOKIE_STORAGE` is misconfigured, pookieStorage raises `PookieStorageConfigError` during startup before any request is served.

## Next step

Go to [Configuration](configuration.md) to set up `POOKIE_STORAGE` and `POOKIE_STORAGE_BACKEND` in your `settings.py`.
