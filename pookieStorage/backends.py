from importlib import import_module

from django.conf import settings
from django.core.files.storage import default_storage

from pookieStorage.exceptions import PookieStorageConfigError


def validateConfig():
    configuredBackends = getattr(settings, 'POOKIE_STORAGE', None)
    activeBackendKey = getattr(settings, 'POOKIE_STORAGE_BACKEND', None)

    # nothing configured - fall back to default_storage silently
    if not configuredBackends and not activeBackendKey:
        return

    if activeBackendKey and activeBackendKey not in (configuredBackends or {}):
        raise PookieStorageConfigError(
            "Backend resolution failed. POOKIE_STORAGE_BACKEND is set to '"
            + activeBackendKey
            + "' but '"
            + activeBackendKey
            + "' is not a key in POOKIE_STORAGE. Available keys are: "
            + str(list((configuredBackends or {}).keys()))
            + ". Check your POOKIE_STORAGE setting in settings.py."
        )

    if configuredBackends and activeBackendKey:
        backendPath = configuredBackends[activeBackendKey]
        try:
            modulePath, className = backendPath.rsplit('.', 1)
            importedModule = import_module(modulePath)
            getattr(importedModule, className)
        except (ImportError, AttributeError):
            raise PookieStorageConfigError(
                "Backend import failed. Could not import '"
                + backendPath
                + "' for backend key '"
                + activeBackendKey
                + "'. Check that the class exists and the dotted path is correct."
            )


def resolveBackend():
    configuredBackends = getattr(settings, 'POOKIE_STORAGE', None)
    activeBackendKey = getattr(settings, 'POOKIE_STORAGE_BACKEND', None)

    # fall back to Django default_storage if POOKIE_STORAGE is not configured
    if not configuredBackends or not activeBackendKey:
        return default_storage

    if activeBackendKey not in configuredBackends:
        raise PookieStorageConfigError(
            "Backend resolution failed. POOKIE_STORAGE_BACKEND is set to '"
            + activeBackendKey
            + "' but '"
            + activeBackendKey
            + "' is not a key in POOKIE_STORAGE. Available keys are: "
            + str(list(configuredBackends.keys()))
            + ". Check your POOKIE_STORAGE setting in settings.py."
        )

    backendPath = configuredBackends[activeBackendKey]

    try:
        modulePath, className = backendPath.rsplit('.', 1)
        importedModule = import_module(modulePath)
        backendClass = getattr(importedModule, className)
        return backendClass()
    except (ImportError, AttributeError):
        raise PookieStorageConfigError(
            "Backend import failed. Could not import '"
            + backendPath
            + "' for backend key '"
            + activeBackendKey
            + "'. Check that the class exists and the dotted path is correct."
        )
