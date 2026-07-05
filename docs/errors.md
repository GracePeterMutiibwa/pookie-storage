# Errors

## DownloadResult

`download()` never raises. It always returns a `DownloadResult` object. Inspect `result.ok` to check whether the download succeeded.

| Attribute | Type | Description |
|---|---|---|
| `ok` | `bool` | `True` if download succeeded, `False` if it did not |
| `path` | `str` or `None` | Full local path to the downloaded file if `ok`, otherwise `None` |
| `error` | `str` or `None` | Human-readable error message if not `ok`, otherwise `None` |
| `file` | `File` or `None` | Open Django `File` object if `ok`, otherwise `None`. Exposes `.name`, `.size`, `.read()` |

## serve() responses

`serve()` never raises. It always returns an HTTP response.

| Status | When |
|---|---|
| 200 | File found and streamed successfully |
| 404 | File field is empty or file not found on the backend |
| 500 | Unexpected backend error |

Error responses have `Content-Type: application/json` and a body with two keys: `error` (a short machine-readable code) and `detail` (a human-readable message).

**404 - no file attached:**

```json
{"error": "no_file", "detail": "No file is attached to this instance."}
```

**404 - file not found on the backend:**

```json
{"error": "file_not_found", "detail": "The file could not be found on the storage backend."}
```

**500 - unexpected backend error:**

```json
{"error": "storage_error", "detail": "An error occurred while retrieving the file."}
```

## Exceptions

Only `PookieStorageConfigError` is raised, and only at startup, never during a request.

```python
from pookieStorage.exceptions import PookieStorageConfigError
```

| Exception | When |
|---|---|
| `PookieStorageConfigError` | `POOKIE_STORAGE_BACKEND` names a key not in `POOKIE_STORAGE`, or the backend dotted path cannot be imported. Raised during `AppConfig.ready()`, before any request is served. |

Both `PookieStorageConfigError` and `PookieStorageDownloadError` are subclasses of `PookieStorageError`, which is a subclass of `Exception`.

## Exception hierarchy

```
Exception
  PookieStorageError
    PookieStorageConfigError
    PookieStorageDownloadError
```
