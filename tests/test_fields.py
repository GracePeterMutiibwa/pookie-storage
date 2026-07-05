import os
from unittest.mock import MagicMock, patch

import pytest
from django.core.files import File as DjangoFile
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, HttpResponse

from pookieStorage.fields import DownloadResult, FileField, PookieFieldFile, PookieFileField


def makeFieldFile(storage, name):
    mockField = MagicMock()
    mockField.storage = storage
    mockField.attname = 'file'
    mockField.max_length = None
    mockField.generate_filename = lambda instance, filename: filename
    mockInstance = MagicMock()
    return PookieFieldFile(mockInstance, mockField, name)


def testDownloadRequiresOutputDir(tmp_path):
    sourceDir = tmp_path / "source"
    sourceDir.mkdir()
    storage = FileSystemStorage(location=str(sourceDir))
    fieldFile = makeFieldFile(storage, 'report.pdf')

    result = fieldFile.download()

    assert result.ok is False
    assert result.path is None
    assert result.file is None
    assert "output_dir" in result.error
    assert "instance.file.download(output_dir=" in result.error


def testDownloadCreatesOutputDirIfMissing(tmp_path):
    sourceDir = tmp_path / "source"
    sourceDir.mkdir()
    testFile = sourceDir / "data.txt"
    testFile.write_bytes(b"hello pookie")

    storage = FileSystemStorage(location=str(sourceDir))
    fieldFile = makeFieldFile(storage, 'data.txt')

    outputDir = str(tmp_path / "new" / "nested" / "dir")
    result = fieldFile.download(output_dir=outputDir)

    assert result.ok is True
    assert os.path.isdir(outputDir)


def testDownloadReturnsCorrectPath(tmp_path):
    sourceDir = tmp_path / "source"
    sourceDir.mkdir()
    testFile = sourceDir / "report.pdf"
    testFile.write_bytes(b"PDF bytes")

    storage = FileSystemStorage(location=str(sourceDir))
    fieldFile = makeFieldFile(storage, 'report.pdf')

    outputDir = str(tmp_path / "output")
    result = fieldFile.download(output_dir=outputDir)

    assert result.ok is True
    assert result.path == os.path.join(outputDir, "report.pdf")
    assert result.error is None


def testDownloadOnLocalBackendCopiesFile(tmp_path):
    sourceDir = tmp_path / "source"
    sourceDir.mkdir()
    originalContent = b"original file content"
    testFile = sourceDir / "archive.zip"
    testFile.write_bytes(originalContent)

    storage = FileSystemStorage(location=str(sourceDir))
    fieldFile = makeFieldFile(storage, 'archive.zip')

    outputDir = str(tmp_path / "output")
    result = fieldFile.download(output_dir=outputDir)

    assert result.ok is True
    copiedPath = result.path
    assert os.path.exists(copiedPath)
    with open(copiedPath, 'rb') as copiedFile:
        assert copiedFile.read() == originalContent


def testDownloadResultFileExposesDjangoFileInterface(tmp_path):
    sourceDir = tmp_path / "source"
    sourceDir.mkdir()
    testFile = sourceDir / "notes.txt"
    testFile.write_bytes(b"test content")

    storage = FileSystemStorage(location=str(sourceDir))
    fieldFile = makeFieldFile(storage, 'notes.txt')

    outputDir = str(tmp_path / "output")
    result = fieldFile.download(output_dir=outputDir)

    assert result.ok is True
    assert isinstance(result.file, DjangoFile)
    assert result.file.name == "notes.txt"
    assert result.file.size > 0


def testServeReturnsFileResponse(tmp_path):
    sourceDir = tmp_path / "source"
    sourceDir.mkdir()
    testFile = sourceDir / "document.pdf"
    testFile.write_bytes(b"PDF content")

    storage = FileSystemStorage(location=str(sourceDir))
    fieldFile = makeFieldFile(storage, 'document.pdf')

    response = fieldFile.serve()

    assert response.status_code == 200
    assert isinstance(response, FileResponse)


def testServeInfersContentType(tmp_path):
    sourceDir = tmp_path / "source"
    sourceDir.mkdir()
    (sourceDir / "image.png").write_bytes(b"\x89PNG\r\n")

    storage = FileSystemStorage(location=str(sourceDir))
    fieldFile = makeFieldFile(storage, 'image.png')

    response = fieldFile.serve()

    assert response.status_code == 200
    assert 'image/png' in response.get('Content-Type', '')


def testDeleteRemovesFile(tmp_path):
    sourceDir = tmp_path / "source"
    sourceDir.mkdir()
    testFile = sourceDir / "todelete.txt"
    testFile.write_bytes(b"bye")

    storage = FileSystemStorage(location=str(sourceDir))
    fieldFile = makeFieldFile(storage, 'todelete.txt')

    assert storage.exists('todelete.txt')
    fieldFile.delete(save=False)
    assert not storage.exists('todelete.txt')


def testEmptyFieldDownloadReturnsErrorResult():
    mockField = MagicMock()
    mockField.storage = MagicMock()
    mockInstance = MagicMock()
    fieldFile = PookieFieldFile(mockInstance, mockField, '')

    result = fieldFile.download(output_dir='/tmp')

    assert result.ok is False
    assert result.path is None
    assert result.file is None
    assert "empty file field" in result.error


def testEmptyFieldServeReturns404():
    mockField = MagicMock()
    mockField.storage = MagicMock()
    mockInstance = MagicMock()
    fieldFile = PookieFieldFile(mockInstance, mockField, '')

    response = fieldFile.serve()

    assert response.status_code == 404
    import json
    body = json.loads(response.content)
    assert body['error'] == 'no_file'


def testUrlReturnsBackendUrl(tmp_path):
    sourceDir = tmp_path / "source"
    sourceDir.mkdir()
    storage = FileSystemStorage(location=str(sourceDir), base_url='/media/')
    fieldFile = makeFieldFile(storage, 'uploads/photo.jpg')

    url = fieldFile.url

    assert 'photo.jpg' in url


def testSaveFromRequest(tmp_path):
    storageDir = tmp_path / "storage"
    storageDir.mkdir()

    from django.core.files.uploadedfile import SimpleUploadedFile

    storage = FileSystemStorage(location=str(storageDir))
    mockField = MagicMock()
    mockField.storage = storage
    mockField.attname = 'file'
    mockField.max_length = None
    mockField.generate_filename = lambda instance, filename: filename
    mockInstance = MagicMock()
    fieldFile = PookieFieldFile(mockInstance, mockField, None)

    uploadedFile = SimpleUploadedFile("uploaded.txt", b"request file content")
    fieldFile.save("uploaded.txt", uploadedFile, save=False)

    assert storage.exists("uploaded.txt")


def testSaveFromLocalPath(tmp_path):
    sourceDir = tmp_path / "source"
    sourceDir.mkdir()
    storageDir = tmp_path / "storage"
    storageDir.mkdir()

    originalFile = sourceDir / "report.pdf"
    originalFile.write_bytes(b"report bytes")

    storage = FileSystemStorage(location=str(storageDir))
    mockField = MagicMock()
    mockField.storage = storage
    mockField.attname = 'file'
    mockField.max_length = None
    mockField.upload_to = ''
    mockField.generate_filename = lambda instance, filename: filename
    mockInstance = MagicMock()
    fieldFile = PookieFieldFile(mockInstance, mockField, None)

    with open(str(originalFile), 'rb') as openedFile:
        fieldFile.save('report.pdf', DjangoFile(openedFile), save=False)

    assert storage.exists('report.pdf')


def testSaveContentFile(tmp_path):
    storageDir = tmp_path / "storage"
    storageDir.mkdir()

    storage = FileSystemStorage(location=str(storageDir))
    mockField = MagicMock()
    mockField.storage = storage
    mockField.attname = 'file'
    mockField.max_length = None
    mockField.generate_filename = lambda instance, filename: filename
    mockInstance = MagicMock()
    fieldFile = PookieFieldFile(mockInstance, mockField, None)

    fieldFile.save('generated.txt', ContentFile(b"generated content"), save=False)

    assert storage.exists('generated.txt')


def testCoexistsWithDjangoNativeFileField():
    from django.db.models import FileField as DjangoNativeFileField
    from pookieStorage.fields import FileField as PookieFileField

    pookieField = PookieFileField(upload_to='uploads/')
    djangoField = DjangoNativeFileField(upload_to='legacy/')

    assert pookieField.attr_class is PookieFieldFile
    assert djangoField.attr_class is not PookieFieldFile


def testFileFieldAliasIsPookieFileField():
    assert FileField is PookieFileField


def testPookieFileFieldAcceptsStorageInstance(tmp_path):
    storageDir = tmp_path / "storage"
    storageDir.mkdir()
    customStorage = FileSystemStorage(location=str(storageDir))

    field = PookieFileField(upload_to='uploads/', storage=customStorage)

    assert field.storage is customStorage


def testPookieFileFieldAcceptsCallableStorage(tmp_path):
    storageDir = tmp_path / "storage"
    storageDir.mkdir()
    customStorage = FileSystemStorage(location=str(storageDir))

    def getStorage():
        return customStorage

    field = PookieFileField(upload_to='uploads/', storage=getStorage)

    assert isinstance(field.storage, FileSystemStorage)
