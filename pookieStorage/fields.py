import json
import mimetypes
import os

from django.core.files import File as DjangoFile
from django.db.models import FileField as DjangoFileField
from django.db.models.fields.files import FieldFile as DjangoFieldFile
from django.http import FileResponse, HttpResponse

from pookieStorage.backends import resolveBackend


class DownloadResult:
    def __init__(self, ok, path, error, file):
        self.ok = ok
        self.path = path
        self.error = error
        self.file = file


class PookieFieldFile(DjangoFieldFile):

    def download(self, output_dir=None):
        if output_dir is None:
            return DownloadResult(
                ok=False,
                path=None,
                error=(
                    "download() requires output_dir. Pass the directory where the file should "
                    "be saved. Example: instance.file.download(output_dir='/tmp/mydir')"
                ),
                file=None,
            )

        if not self.name:
            return DownloadResult(
                ok=False,
                path=None,
                error="download() called on an empty file field. No file is attached to this instance.",
                file=None,
            )

        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as creationError:
            return DownloadResult(
                ok=False,
                path=None,
                error=(
                    "download() could not create output_dir '"
                    + output_dir
                    + "'. Error: "
                    + str(creationError)
                    + ". Check that the path is valid and you have write permissions."
                ),
                file=None,
            )

        fileName = os.path.basename(self.name)
        localPath = os.path.join(output_dir, fileName)

        try:
            with self.storage.open(self.name, 'rb') as storageFileHandle:
                with open(localPath, 'wb') as localFileHandle:
                    chunkSize = 65536
                    while True:
                        chunk = storageFileHandle.read(chunkSize)
                        if not chunk:
                            break
                        localFileHandle.write(chunk)
        except Exception as downloadError:
            if os.path.exists(localPath):
                try:
                    os.remove(localPath)
                except OSError:
                    pass
            return DownloadResult(
                ok=False,
                path=None,
                error=(
                    "File download failed for '"
                    + self.name
                    + "'. The request to the storage backend returned an error: "
                    + str(downloadError)
                    + ". Check your storage backend credentials and endpoint configuration."
                ),
                file=None,
            )

        openedFileHandle = open(localPath, 'rb')
        djangoFile = DjangoFile(openedFileHandle, name=os.path.basename(localPath))

        return DownloadResult(ok=True, path=localPath, error=None, file=djangoFile)

    def serve(self):
        if not self.name:
            return HttpResponse(
                json.dumps({"error": "no_file", "detail": "No file is attached to this instance."}),
                content_type='application/json',
                status=404,
            )

        try:
            storageFileHandle = self.storage.open(self.name, 'rb')
            contentType, _ = mimetypes.guess_type(self.name)
            if contentType is None:
                contentType = 'application/octet-stream'
            return FileResponse(storageFileHandle, content_type=contentType)
        except FileNotFoundError:
            return HttpResponse(
                json.dumps({
                    "error": "file_not_found",
                    "detail": "The file could not be found on the storage backend.",
                }),
                content_type='application/json',
                status=404,
            )
        except Exception:
            return HttpResponse(
                json.dumps({
                    "error": "storage_error",
                    "detail": "An error occurred while retrieving the file.",
                }),
                content_type='application/json',
                status=500,
            )


class PookieFileField(DjangoFileField):
    attr_class = PookieFieldFile

    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, **kwargs):
        if storage is None:
            resolvedStorage = resolveBackend()
        elif callable(storage):
            # call it now so Django 3.2 gets an instance, not a callable
            resolvedStorage = storage()
        else:
            resolvedStorage = storage
        super().__init__(
            verbose_name=verbose_name,
            name=name,
            upload_to=upload_to,
            storage=resolvedStorage,
            **kwargs,
        )


# public name - developers import this
FileField = PookieFileField
