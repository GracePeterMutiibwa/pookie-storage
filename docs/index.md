# pookieStorage

A Django storage field that works everywhere. One import. Any backend. Zero plumbing.

pookieStorage gives you a `FileField` that is a full superset of Django's native `FileField`. Every argument, every attribute, and every method Django's `FileField` supports works identically. On top of that you get two methods: `download()` to pull a file to a local path regardless of backend, and `serve()` to stream a file directly from a view.

The backend is a config detail. You set `POOKIE_STORAGE_BACKEND` once in `settings.py`. Every `FileField` in your project routes through it automatically. Switch from local to R2 to S3 by changing one value.

## What pookieStorage does

- Routes file saves, reads, and deletes to the configured backend
- Provides `download()` - copies a file to a local directory from any backend, local or cloud, with a consistent interface
- Provides `serve()` - returns a streaming `FileResponse` ready to return from a Django view
- Validates your `POOKIE_STORAGE` config at startup and raises a clear error before any request is served

## What pookieStorage does not do

- It does not configure storage backends. Your existing `S3Boto3Storage`, `FileSystemStorage`, or any other Django-compatible storage class works as-is.
- It does not rewrite or alter URLs. The backend's URL is the URL.
- It does not depend on django-storages, boto3, or any cloud SDK.

## Get started

See [Installation](installation.md) to add pookieStorage to your project, then [Configuration](configuration.md) to wire up your backends.
