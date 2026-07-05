# Configuration

All pookieStorage configuration goes in `settings.py` alongside your existing Django settings.

## Settings

```python
# settings.py

POOKIE_STORAGE = {
    "local": "core.storage.LocalStorage",
    "cloud": "core.storage.MediaStorage",
}

POOKIE_STORAGE_BACKEND = "cloud"
```

### POOKIE_STORAGE

A dictionary of named backends. Each key is a name you choose. Each value is a dotted import path to a storage class in your project. The class must exist and be importable at startup.

### POOKIE_STORAGE_BACKEND

The name of the active backend. Must match a key in `POOKIE_STORAGE`. Every `FileField` in your project routes through this backend. To switch environments, change this one value.

## Fallback behavior

If neither `POOKIE_STORAGE` nor `POOKIE_STORAGE_BACKEND` is set in your settings, pookieStorage falls back to Django's `default_storage`. The field works normally. No error is raised.

## Coexistence with Django's STORAGES setting

pookieStorage reads only `POOKIE_STORAGE` and `POOKIE_STORAGE_BACKEND`. It never reads or modifies Django's `STORAGES` setting and does not interfere with staticfiles routing or the `default` storage key.

## Startup validation

pookieStorage validates `POOKIE_STORAGE` and `POOKIE_STORAGE_BACKEND` during `AppConfig.ready()`, which runs at Django startup before any request is served.

**If `POOKIE_STORAGE_BACKEND` points to a key that does not exist in `POOKIE_STORAGE`:**

```
PookieStorageConfigError: Backend resolution failed. POOKIE_STORAGE_BACKEND is set to 'cloud'
but 'cloud' is not a key in POOKIE_STORAGE. Available keys are: ['local'].
Check your POOKIE_STORAGE setting in settings.py.
```

**If the dotted path for the active backend cannot be imported:**

```
PookieStorageConfigError: Backend import failed. Could not import 'core.storage.DoesNotExist'
for backend key 'cloud'. Check that the class exists and the dotted path is correct.
```

Both errors name exactly what went wrong and what to check.
