import pytest
from django.test import override_settings

from pookieStorage.backends import resolveBackend, validateConfig
from pookieStorage.exceptions import PookieStorageConfigError


def testValidConfigResolvesBackend():
    with override_settings(
        POOKIE_STORAGE={"local": "django.core.files.storage.FileSystemStorage"},
        POOKIE_STORAGE_BACKEND="local",
    ):
        resolvedBackend = resolveBackend()
        from django.core.files.storage import FileSystemStorage
        assert isinstance(resolvedBackend, FileSystemStorage)


def testMissingBackendKeyRaisesConfigError():
    with override_settings(
        POOKIE_STORAGE={"local": "django.core.files.storage.FileSystemStorage"},
        POOKIE_STORAGE_BACKEND="cloud",
    ):
        with pytest.raises(PookieStorageConfigError) as errorInfo:
            resolveBackend()
        assert "cloud" in str(errorInfo.value)
        assert "local" in str(errorInfo.value)
        assert "POOKIE_STORAGE" in str(errorInfo.value)


def testBadImportPathRaisesConfigError():
    with override_settings(
        POOKIE_STORAGE={"cloud": "django.core.files.storage.DoesNotExistStorage"},
        POOKIE_STORAGE_BACKEND="cloud",
    ):
        with pytest.raises(PookieStorageConfigError) as errorInfo:
            resolveBackend()
        assert "DoesNotExistStorage" in str(errorInfo.value)
        assert "cloud" in str(errorInfo.value)


def testFallsBackToDefaultStorageWhenNotConfigured():
    with override_settings():
        # remove POOKIE_STORAGE and POOKIE_STORAGE_BACKEND if they exist
        from django.conf import settings
        originalStorage = getattr(settings, 'POOKIE_STORAGE', None)
        originalBackend = getattr(settings, 'POOKIE_STORAGE_BACKEND', None)

        # clear both settings
        if hasattr(settings, 'POOKIE_STORAGE'):
            delattr(settings, 'POOKIE_STORAGE')
        if hasattr(settings, 'POOKIE_STORAGE_BACKEND'):
            delattr(settings, 'POOKIE_STORAGE_BACKEND')

        try:
            from django.core.files.storage import default_storage
            resolvedBackend = resolveBackend()
            assert resolvedBackend is default_storage
        finally:
            if originalStorage is not None:
                settings.POOKIE_STORAGE = originalStorage
            if originalBackend is not None:
                settings.POOKIE_STORAGE_BACKEND = originalBackend


def testValidateConfigPassesForValidSettings():
    with override_settings(
        POOKIE_STORAGE={"local": "django.core.files.storage.FileSystemStorage"},
        POOKIE_STORAGE_BACKEND="local",
    ):
        # no exception raised
        validateConfig()


def testValidateConfigRaisesForMissingKey():
    with override_settings(
        POOKIE_STORAGE={"local": "django.core.files.storage.FileSystemStorage"},
        POOKIE_STORAGE_BACKEND="cloud",
    ):
        with pytest.raises(PookieStorageConfigError):
            validateConfig()


def testValidateConfigRaisesForBadImportPath():
    with override_settings(
        POOKIE_STORAGE={"cloud": "no.such.module.Storage"},
        POOKIE_STORAGE_BACKEND="cloud",
    ):
        with pytest.raises(PookieStorageConfigError):
            validateConfig()


def testValidateConfigPassesWhenNothingConfigured():
    from django.conf import settings
    if hasattr(settings, 'POOKIE_STORAGE'):
        delattr(settings, 'POOKIE_STORAGE')
    if hasattr(settings, 'POOKIE_STORAGE_BACKEND'):
        delattr(settings, 'POOKIE_STORAGE_BACKEND')
    # no exception raised
    validateConfig()
