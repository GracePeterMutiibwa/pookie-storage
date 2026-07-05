from django.apps import AppConfig


class PookieStorageConfig(AppConfig):
    name = 'pookieStorage'

    def ready(self):
        from pookieStorage.backends import validateConfig
        validateConfig()
