import pytest

from pookieStorage.exceptions import (
    PookieStorageConfigError,
    PookieStorageDownloadError,
    PookieStorageError,
)


def testPookieStorageErrorIsException():
    assert issubclass(PookieStorageError, Exception)


def testPookieStorageConfigErrorIsPookieStorageError():
    assert issubclass(PookieStorageConfigError, PookieStorageError)


def testPookieStorageDownloadErrorIsPookieStorageError():
    assert issubclass(PookieStorageDownloadError, PookieStorageError)


def testPookieStorageConfigErrorCanBeRaised():
    with pytest.raises(PookieStorageConfigError, match="test message"):
        raise PookieStorageConfigError("test message")


def testPookieStorageDownloadErrorCanBeRaised():
    with pytest.raises(PookieStorageDownloadError, match="download failed"):
        raise PookieStorageDownloadError("download failed")


def testPookieStorageConfigErrorCaughtAsPookieStorageError():
    with pytest.raises(PookieStorageError):
        raise PookieStorageConfigError("caught as base")


def testPookieStorageDownloadErrorCaughtAsPookieStorageError():
    with pytest.raises(PookieStorageError):
        raise PookieStorageDownloadError("caught as base")
