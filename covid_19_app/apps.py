from django.apps import AppConfig


class Covid19AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'covid_19_app'

    def ready(self):
        print("start")
        #from covid_19_app.utils import get_daily_data
        #get_daily_data()
        #from covid_19_app.scheluder import covid_api_scheduler 
        #covid_api_scheduler.start_scheluer()
