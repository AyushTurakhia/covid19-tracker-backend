from django.db import models


class StateCovidData(models.Model):
    state_code = models.CharField(max_length=10, null=True, blank=True)
    state_name = models.CharField(max_length=255, null=True, blank=True)
    dates_data = models.JSONField()
    note = models.TextField(null=True, blank=True)
    population = models.IntegerField(default=0,null=True)
    last_update = models.DateTimeField()

    def __str__(self):
        return str(self.state_code) + " " + str(self.state_name)


'''
dates_data format 
date eg:"2021-09-28"
{
    date:{
        "confirm": 0,
        "recovered": 0,
        "deaths": 0,
        "tested": 0,
        "active": confirm - (recovered + deaths),
        "total_confirm": 0,
        "total_recovered": 0,
        "total_death": 0,
        "total_tested": 0,
        "total_active":total_confirm - (total_recovered + total_deaths),
        "total_vaccinated1": 0,
        "total_vaccinated2": 0,
    }
}
'''
