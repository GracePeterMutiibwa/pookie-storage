# The Field

pookieStorage exports a single field: `FileField`.

```python
from pookieStorage.fields import FileField
```

This is a full superset of Django's native `FileField`. Every argument Django's `FileField` accepts works identically. The only change in existing code is the import line.

```python
# before
from django.db.models import FileField

# after
from pookieStorage.fields import FileField
```

## Basic usage

```python
from django.db import models
from pookieStorage.fields import FileField


class Document(models.Model):
    file = FileField(upload_to='uploads/')
```

Files land in `uploads/` on whichever backend `POOKIE_STORAGE_BACKEND` points to.

## With a callable upload_to

```python
from django.db import models
from pookieStorage.fields import FileField


def assignLocation(instance, filename):
    return f"users/{instance.owner.pk}/{filename}"


class Document(models.Model):
    file = FileField(upload_to=assignLocation)
```

## With a callable storage override

```python
from django.conf import settings
from django.db import models
from pookieStorage.fields import FileField


def getStorage():
    if settings.DEBUG:
        return LocalStorage()
    return R2MediaStorage()


class Document(models.Model):
    file = FileField(upload_to='uploads/', storage=getStorage)
```

When `storage` is provided on the field, it takes full precedence over `POOKIE_STORAGE_BACKEND` for that field only. Most models will never need this.

## With blank and null

```python
from django.db import models
from pookieStorage.fields import FileField


class Document(models.Model):
    file = FileField(upload_to='uploads/', blank=True, null=True)
```

## Full model example

```python
from uuid import uuid4
from django.db import models
from django.contrib.auth import get_user_model
from pookieStorage.fields import FileField

User = get_user_model()


def assignNameAndLocation(instance, filename):
    return f"users/{instance.fileOwner.pk}/{uuid4()}/{filename}"


class FileItem(models.Model):
    fileTag = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    fileName = models.TextField()
    fileField = FileField(upload_to=assignNameAndLocation)
    fileOwner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_files")
    uploadedDate = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-uploadedDate",)
```

## Saving files

**From a request:**

```python
instance.file = request.FILES["file"]
instance.save()
```

**From a ContentFile:**

```python
from django.core.files.base import ContentFile

instance.file = ContentFile(b"file bytes", name="report.pdf")
instance.save()
```

**From a local path:**

```python
from django.core.files import File

with open("/tmp/report.pdf", "rb") as f:
    instance.file.save("report.pdf", File(f))
```

## Using alongside Django's native FileField

```python
from django.db import models
from django.db.models import FileField as DjangoFileField
from pookieStorage.fields import FileField as PookieFileField


class Document(models.Model):
    legacyFile = DjangoFileField(upload_to='legacy/')
    newFile = PookieFileField(upload_to='uploads/')
```

Both fields coexist without conflict.
