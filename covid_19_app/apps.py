from django.apps import AppConfig


class Covid19AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'covid_19_app'

    def ready(self):
        print("ok")
        from covid_19_app.scheluder import covid_api_scheduler 
        covid_api_scheduler.start_scheluer()
