# Deployment

## Building the package

Install build tools:

```bash
pip install build
```

Build the distribution:

```bash
python -m build
```

This produces two files in `dist/`:

- `pookie_storage-0.1.0.tar.gz` - source distribution
- `pookie_storage-0.1.0-py3-none-any.whl` - wheel

## Publishing to PyPI

Install Twine:

```bash
pip install twine
```

Upload to PyPI:

```bash
twine upload dist/*
```

You will be prompted for your PyPI credentials. To use an API token instead of a password, set `__token__` as the username and paste the token as the password.

## Publishing to TestPyPI

To test the release process before publishing to the real index:

```bash
twine upload --repository testpypi dist/*
```

Install from TestPyPI to verify:

```bash
pip install --index-url https://test.pypi.org/simple/ pookie-storage
```

## Building the documentation site

Install MkDocs with the Material theme:

```bash
pip install mkdocs mkdocs-material
```

Preview locally:

```bash
mkdocs serve
```

Build the static site:

```bash
mkdocs build
```

The static site is written to `site/`.

## Hosting documentation on Read the Docs

The repository includes `.readthedocs.yaml` at the project root. Connect the repository to Read the Docs and it will build and host the documentation automatically on every push to the default branch.

The `.readthedocs.yaml` configuration specifies Python 3.10, MkDocs with the Material theme, and installs dependencies from `docs/requirements.txt`.

## Running the test suite

Install dev dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=pookieStorage --cov-report=term-missing
```
