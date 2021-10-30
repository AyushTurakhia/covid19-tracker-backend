from django.urls import path,re_path
from covid_19_app.views import *

urlpatterns = [
    path('',home,name="home"),
    path('all_state_total_data/', total_data_all_states, name="total data"),
    path('get_data/', get_data, name="get data"),
    re_path(r'^total_data_state/(?P<code>[A-Z]{2})/$', total_data_states,name="state wise total data"),
    path('statewise_timeseries_data/', statewise_timeseries_data, name="state wise time series"),

    path('get_charbot_data/', get_charbot_data, name="chatbot data"),

    path('chat_bot/', chat_bot, name="chatbot data"),
]
