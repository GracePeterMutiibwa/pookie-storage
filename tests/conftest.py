import django
from django.conf import settings


def pytest_configure(config):
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'pookieStorage',
        ],
        DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
        USE_TZ=True,
        # no POOKIE_STORAGE or POOKIE_STORAGE_BACKEND set - tests override as needed
    )
