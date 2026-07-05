# Edge Cases

## File field is empty

```python
instance.file.url
# raises ValueError - consistent with Django's native FileField behavior

result = instance.file.download(output_dir="/tmp")
# result.ok    -> False
# result.error -> "download() called on an empty file field. No file is attached to this instance."
# result.path  -> None
# result.file  -> None

response = instance.file.serve()
# returns HttpResponse with status 404
# body: {"error": "no_file", "detail": "No file is attached to this instance."}
```

## download() called without output_dir

```python
result = instance.file.download()
# result.ok    -> False
# result.error -> "download() requires output_dir. Pass the directory where the file should be saved. Example: instance.file.download(output_dir='/tmp/mydir')"
# result.path  -> None
# result.file  -> None
```

## serve() when the file is missing from the backend

```python
response = instance.file.serve()
# returns HttpResponse with status 404
# body: {"error": "file_not_found", "detail": "The file could not be found on the storage backend."}
```

## serve() when the backend throws an unexpected error

```python
response = instance.file.serve()
# returns HttpResponse with status 500
# body: {"error": "storage_error", "detail": "An error occurred while retrieving the file."}
```

## POOKIE_STORAGE_BACKEND points to a missing key

```python
POOKIE_STORAGE = {"local": "core.storage.LocalStorage"}
POOKIE_STORAGE_BACKEND = "cloud"
```

Raises at startup:

```
PookieStorageConfigError: Backend resolution failed. POOKIE_STORAGE_BACKEND is set to 'cloud'
but 'cloud' is not a key in POOKIE_STORAGE. Available keys are: ['local'].
Check your POOKIE_STORAGE setting in settings.py.
```

## POOKIE_STORAGE backend path cannot be imported

```python
POOKIE_STORAGE = {"cloud": "core.storage.DoesNotExist"}
POOKIE_STORAGE_BACKEND = "cloud"
```

Raises at startup:

```
PookieStorageConfigError: Backend import failed. Could not import 'core.storage.DoesNotExist'
for backend key 'cloud'. Check that the class exists and the dotted path is correct.
```

## Neither POOKIE_STORAGE nor POOKIE_STORAGE_BACKEND is set

pookieStorage falls back to Django's `default_storage`. The field works normally.

## output_dir does not exist

```python
instance.file.download(output_dir="/tmp/doesnotexist")
```

pookieStorage creates the directory before downloading. No error is raised.

## download() on a local backend

```python
result = instance.file.download(output_dir="/tmp/work")
```

On a local backend the file already lives on disk. pookieStorage copies it to `output_dir` rather than making a network request. The interface is identical to a cloud backend.

## download() fails due to a storage error

When the storage backend raises an exception during download, `result.ok` is `False` and `result.error` contains a message in this form:

```
File download failed for 'media/uploads/report.pdf'.
The request to the storage backend returned an error: <original error>.
Check your storage backend credentials and endpoint configuration.
```

Any partial file written to `output_dir` is deleted before `result` is returned.

## serve() with a large file

`serve()` uses Django's `FileResponse` which streams the response. The file is never fully loaded into memory regardless of size.

## Replacing a file on an existing instance

```python
instance.file = request.FILES["newfile"]
instance.save()
```

The old file is not automatically deleted from storage. This is consistent with Django's native `FileField` behavior. To delete the old file first:

```python
instance.file.delete()
instance.file = request.FILES["newfile"]
instance.save()
```

## File with the same name already exists in storage

Controlled entirely by the backend's `file_overwrite` setting. pookieStorage does not interfere.

## Using pookieStorage alongside Django's native FileField

```python
from django.db import models
from django.db.models import FileField as DjangoFileField
from pookieStorage.fields import FileField as PookieFileField


class Document(models.Model):
    legacyFile = DjangoFileField(upload_to='legacy/')
    newFile = PookieFileField(upload_to='uploads/')
```

Both coexist without conflict.

## Using pookieStorage without django-storages

pookieStorage has no dependency on django-storages. If the active backend is Django's built-in `FileSystemStorage`, everything works. django-storages is only needed if your own storage classes use it.
