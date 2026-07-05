# pookieStorage

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/pookie-storage/badge/?version=latest)](https://pookie-storage.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://img.shields.io/pypi/v/pookie-storage.svg)](https://pypi.org/project/pookie-storage/)

A Django storage field that works everywhere. One import. Any backend. Zero plumbing.

## Installation

pip install pookie-storage

## Quick start

Add to INSTALLED_APPS:

    INSTALLED_APPS = [
        ...
        "pookieStorage",
    ]

Configure your backends in settings.py:

    POOKIE_STORAGE = {
        "local": "core.storage.LocalStorage",
        "cloud": "core.storage.MediaStorage",
    }

    POOKIE_STORAGE_BACKEND = "cloud"

Swap the import in your models:

    from pookieStorage.fields import FileField

That is it. Your models, views, and business logic stay exactly the same.

## License

MIT
