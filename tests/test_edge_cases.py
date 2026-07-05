import json
import os
from unittest.mock import MagicMock, patch

import pytest
from django.core.files.storage import FileSystemStorage

from pookieStorage.fields import PookieFieldFile


def makeFieldFile(storage, name):
    mockField = MagicMock()
    mockField.storage = storage
    mockField.attname = 'file'
    mockField.max_length = None
    mockField.generate_filename = lambda instance, filename: filename
    mockInstance = MagicMock()
    return PookieFieldFile(mockInstance, mockField, name)


def testReplaceFileDoesNotDeleteOldFile(tmp_path):
    storageDir = tmp_path / "storage"
    storageDir.mkdir()
    (storageDir / "original.txt").write_bytes(b"original")

    storage = FileSystemStorage(location=str(storageDir))
    fieldFile = makeFieldFile(storage, 'original.txt')

    # save a new file without deleting the old one first
    from django.core.files.base import ContentFile
    fieldFile.save('replacement.txt', ContentFile(b"new content"), save=False)

    # original file still exists
    assert storage.exists('original.txt')


def testDownloadNetworkFailureCleansUpPartialFile(tmp_path):
    outputDir = str(tmp_path / "output")

    brokenStorage = MagicMock()
    brokenStorage.open.side_effect = IOError("connection refused")

    fieldFile = makeFieldFile(brokenStorage, 'uploads/report.pdf')

    # create a partial file to simulate interrupted download
    os.makedirs(outputDir, exist_ok=True)
    partialFilePath = os.path.join(outputDir, 'report.pdf')
    with open(partialFilePath, 'wb') as partialFile:
        partialFile.write(b"partial")

    result = fieldFile.download(output_dir=outputDir)

    assert result.ok is False
    assert "report.pdf" in result.error
    assert "connection refused" in result.error
    # partial file cleaned up
    assert not os.path.exists(partialFilePath)


def testLargeFileServeDoesNotLoadIntoMemory(tmp_path):
    sourceDir = tmp_path / "source"
    sourceDir.mkdir()
    largeFile = sourceDir / "large.bin"
    largeFile.write_bytes(b"x" * 10 * 1024 * 1024)  # 10 MB

    storage = FileSystemStorage(location=str(sourceDir))
    fieldFile = makeFieldFile(storage, 'large.bin')

    response = fieldFile.serve()

    # FileResponse is a streaming response - file is never fully loaded into memory
    from django.http import FileResponse
    assert isinstance(response, FileResponse)
    assert response.status_code == 200


def testDownloadOnCloudBackend(tmp_path):
    outputDir = str(tmp_path / "output")
    fileContent = b"cloud file content"

    import io
    cloudFileObject = io.BytesIO(fileContent)

    # context manager protocol
    mockContextResult = MagicMock()
    mockContextResult.read = cloudFileObject.read
    mockContextResult.__enter__ = lambda self: self
    mockContextResult.__exit__ = MagicMock(return_value=False)

    mockStorage = MagicMock()
    mockStorage.open.return_value = mockContextResult

    fieldFile = makeFieldFile(mockStorage, 'media/uploads/report.pdf')

    result = fieldFile.download(output_dir=outputDir)

    assert result.ok is True
    assert result.path is not None
    assert os.path.exists(result.path)
    with open(result.path, 'rb') as downloadedFile:
        assert downloadedFile.read() == fileContent


def testServeReturns404WhenFileNotFoundOnBackend(tmp_path):
    sourceDir = tmp_path / "source"
    sourceDir.mkdir()
    storage = FileSystemStorage(location=str(sourceDir))

    # name points to a file that does not exist in storage
    fieldFile = makeFieldFile(storage, 'missing.pdf')

    response = fieldFile.serve()

    assert response.status_code == 404
    body = json.loads(response.content)
    assert body['error'] == 'file_not_found'
    assert 'storage backend' in body['detail']


def testServeReturns500OnUnexpectedBackendError():
    brokenStorage = MagicMock()
    brokenStorage.open.side_effect = RuntimeError("unexpected backend failure")

    fieldFile = makeFieldFile(brokenStorage, 'uploads/data.csv')

    response = fieldFile.serve()

    assert response.status_code == 500
    body = json.loads(response.content)
    assert body['error'] == 'storage_error'


def testDownloadOutputDirCreatedWhenMissing(tmp_path):
    sourceDir = tmp_path / "source"
    sourceDir.mkdir()
    (sourceDir / "file.txt").write_bytes(b"content")

    storage = FileSystemStorage(location=str(sourceDir))
    fieldFile = makeFieldFile(storage, 'file.txt')

    deepOutputDir = str(tmp_path / "a" / "b" / "c")
    assert not os.path.exists(deepOutputDir)

    result = fieldFile.download(output_dir=deepOutputDir)

    assert result.ok is True
    assert os.path.isdir(deepOutputDir)


def testDownloadEmptyFieldWithOutputDir():
    mockField = MagicMock()
    mockField.storage = MagicMock()
    mockInstance = MagicMock()
    fieldFile = PookieFieldFile(mockInstance, mockField, '')

    result = fieldFile.download(output_dir='/tmp')

    assert result.ok is False
    assert "empty file field" in result.error
    assert result.path is None
    assert result.file is None


def testServeEmptyFieldReturns404WithNoFileBody():
    mockField = MagicMock()
    mockField.storage = MagicMock()
    mockInstance = MagicMock()
    fieldFile = PookieFieldFile(mockInstance, mockField, '')

    response = fieldFile.serve()

    assert response.status_code == 404
    body = json.loads(response.content)
    assert body['error'] == 'no_file'
    assert 'No file is attached' in body['detail']
