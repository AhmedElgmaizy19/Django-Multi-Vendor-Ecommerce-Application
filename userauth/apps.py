from django.apps import AppConfig



class UserauthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'userauth'

    def ready(self):
        import userauth.signals
        # This will ensure that the signals are imported and ready to use when the app is loaded.
        # You can also import other modules or perform other initialization tasks here if needed.