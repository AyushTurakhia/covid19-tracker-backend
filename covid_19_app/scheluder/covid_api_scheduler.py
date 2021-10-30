from apscheduler import schedulers
from apscheduler.schedulers.background import BackgroundScheduler
from covid_19_app.utils import *

def start_scheluer():
    scheduler = BackgroundScheduler()
    scheduler.add_job(get_daily_data,trigger='cron', hour='15', minute='45',id="covid_027",replace_existing=True)
    scheduler.start()
