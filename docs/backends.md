# Setting Up Backends

pookieStorage does not configure storage backends. You configure your storage classes exactly as you always have. pookieStorage reads the class name from `POOKIE_STORAGE` and uses it.

## Cloudflare R2

```python
# core/storage.py
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage
import os


class LocalStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(
            location=os.path.join(settings.BASE_DIR, "media"),
            *args,
            **kwargs,
        )


class R2MediaStorage(S3Boto3Storage):
    location = "media"
    file_overwrite = False
    querystring_auth = True
    default_acl = None
    signature_version = "s3v4"
    expiration = 3600

    def __init__(self, *args, **kwargs):
        self.bucket_name = os.environ.get("CLOUDFLARE_R2_MEDIA_BUCKET_NAME")
        self.custom_domain = None
        super().__init__(*args, **kwargs)
```

```python
# settings.py
import os

AWS_ACCESS_KEY_ID = os.environ.get("CLOUDFLARE_R2_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("CLOUDFLARE_R2_SECRET_ACCESS_KEY")
AWS_S3_ENDPOINT_URL = os.environ.get("CLOUDFLARE_R2_ENDPOINT")
AWS_S3_REGION_NAME = "auto"
AWS_S3_FILE_OVERWRITE = False

POOKIE_STORAGE = {
    "local": "core.storage.LocalStorage",
    "cloud": "core.storage.R2MediaStorage",
}

POOKIE_STORAGE_BACKEND = "cloud"
```

## AWS S3

```python
# core/storage.py
from storages.backends.s3boto3 import S3Boto3Storage


class S3MediaStorage(S3Boto3Storage):
    location = "media"
    file_overwrite = False
    querystring_auth = True
```

```python
# settings.py
import os

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")

POOKIE_STORAGE = {
    "local": "core.storage.LocalStorage",
    "cloud": "core.storage.S3MediaStorage",
}

POOKIE_STORAGE_BACKEND = "cloud"
```

## Projects without django-storages

pookieStorage has no dependency on django-storages. If your backend is Django's built-in `FileSystemStorage`, everything works. django-storages is only needed when your own storage classes use it.

## Any Django-compatible storage

Any class that implements Django's storage interface works as a pookieStorage backend. Pass its dotted path as a value in `POOKIE_STORAGE` and pookieStorage will import and instantiate it at startup.
