# API Reference

## FileField

```python
from pookieStorage.fields import FileField
```

A subclass of Django's `FileField`. Accepts all the same arguments.

| Argument | Type | Description |
|---|---|---|
| `upload_to` | `str` or callable | Upload path, passed directly to Django's `FileField` |
| `storage` | storage instance, callable, or omitted | When provided, takes precedence over `POOKIE_STORAGE_BACKEND` for this field only |
| `max_length` | `int` | Maximum length of the stored file name |
| `blank` | `bool` | Whether the field is allowed to be blank |
| `null` | `bool` | Whether the database column allows NULL |

When `storage` is omitted, the backend configured by `POOKIE_STORAGE_BACKEND` is used.

---

## FieldFile methods

Accessing `instance.file` on a model with a `FileField` returns a `PookieFieldFile` instance. It exposes everything Django's `FieldFile` exposes, plus `download()` and `serve()`.

### Standard Django FieldFile attributes

```python
instance.file.name   # relative path stored in the database column
instance.file.url    # URL returned by the active backend
instance.file.size   # file size in bytes
```

### Standard Django FieldFile methods

```python
instance.file.open(mode='rb')
instance.file.read()
instance.file.close()
instance.file.save(name, content, save=True)
instance.file.delete(save=True)
```

---

### download(output_dir)

Downloads the file to a local directory. Works the same whether the backend is local or cloud.

```python
result = instance.file.download(output_dir="/tmp/processing")
```

`download()` never raises. It always returns a `DownloadResult` object.

**DownloadResult attributes:**

| Attribute | Type | Description |
|---|---|---|
| `ok` | `bool` | `True` if the download succeeded |
| `path` | `str` or `None` | Full local path to the downloaded file if `ok`, otherwise `None` |
| `error` | `str` or `None` | Error message if not `ok`, otherwise `None` |
| `file` | `File` or `None` | Open Django `File` object if `ok`, otherwise `None`. Exposes `.name`, `.size`, `.read()` |

**Typical usage:**

```python
result = instance.file.download(output_dir="/tmp/work")

if result.ok:
    convert(result.path)
    print(result.file.size)
    os.remove(result.path)
else:
    logger.error(result.error)
```

`output_dir` is required. If omitted, `result.ok` is `False` and `result.error` explains what to pass.

pookieStorage creates `output_dir` if it does not exist. Cleanup of the downloaded file after use is the caller's responsibility.

---

### serve()

Returns a streaming `FileResponse` ready to return from a Django view.

```python
def fileDownloadView(request, pk):
    doc = Document.objects.get(pk=pk)
    return doc.file.serve()
```

`serve()` never raises. It always returns an HTTP response.

| Status | When |
|---|---|
| 200 | File found and streamed to the client |
| 404 | File field is empty or file not found on the backend |
| 500 | Unexpected backend error |

Content-Type is inferred from the file name. The file is never fully loaded into memory regardless of size.

---

## Exceptions

```python
from pookieStorage.exceptions import PookieStorageConfigError
```

| Exception | When |
|---|---|
| `PookieStorageConfigError` | Raised at startup when `POOKIE_STORAGE` or `POOKIE_STORAGE_BACKEND` is misconfigured. Never raised during a request. |

`PookieStorageConfigError` is a subclass of `PookieStorageError`, which is a subclass of `Exception`.
