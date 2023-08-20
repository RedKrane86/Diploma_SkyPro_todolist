from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Класс настроек для пользователя
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
