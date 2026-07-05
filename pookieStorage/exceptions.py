class PookieStorageError(Exception):
    pass


class PookieStorageConfigError(PookieStorageError):
    pass


class PookieStorageDownloadError(PookieStorageError):
    pass
