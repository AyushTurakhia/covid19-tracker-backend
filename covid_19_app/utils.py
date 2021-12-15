from datetime import date, timedelta, datetime
import requests
from pytz import timezone
from covid_19_app.models import StateCovidData

def getStates():
    states = {
        "AN": "Andaman and Nicobar Islands",
        "AP": "Andhra Pradesh",
        "AR": "Arunachal Pradesh",
        "AS": "Assam",
        "BR": "Bihar",
        "CH": "Chandigarh",
        "CT": "Chhattisgarh",
        "DN": "Dadra and Nagar Haveli",
        "DD": "Daman and Diu",
        "DL": "Delhi",
        "GA": "Goa",
        "GJ": "Gujarat",
        "HR": "Haryana",
        "HP": "Himachal Pradesh",
        "JK": "Jammu and Kashmir",
        "JH": "Jharkhand",
        "KA": "Karnataka",
        "KL": "Kerala",
        "LA": "Ladakh",
        "LD": "Lakshadweep",
        "MP": "Madhya Pradesh",
        "MH": "Maharashtra",
        "MN": "Manipur",
        "ML": "Meghalaya",
        "MZ": "Mizoram",
        "NL": "Nagaland",
        "OR": "Odisha",
        "PY": "Puducherry",
        "PB": "Punjab",
        "RJ": "Rajasthan",
        "SK": "Sikkim",
        "TN": "Tamil Nadu",
        "TG": "Telangana",
        "TR": "Tripura",
        "UP": "Uttar Pradesh",
        "UT": "Uttarakhand",
        "WB": "West Bengal",
        "IN": "India"
    }
    return states


def collect_previous_data():
    
    min_date = date.today() - timedelta(days=200)
    data = requests.get("https://data.covid19india.org/v4/min/timeseries.min.json")
    json_data = data.json()
    state_details = getStates()
    for state_code in json_data.keys():
        dates_data = json_data[state_code]["dates"]
        if state_code != 'UN':
            state = state_code if state_code != 'TT' else "IN"
            state_name = state_details[state]
            dates_data_json = {}
            for d in dates_data.keys():
                
                if d >= str(min_date):
                    date_data = dates_data[d]
                    current = {
                        "confirm": 0,
                        "recovered": 0,
                        "deaths": 0,
                        "tested": 0
                    }
                    if "delta" in date_data.keys():
                        delta_data = date_data["delta"]
                        if "confirmed" in delta_data.keys():
                            current["confirm"] = delta_data["confirmed"]
                        if "deceased" in delta_data.keys():
                            current["deaths"] = delta_data["deceased"]
                        if "recovered" in delta_data.keys():
                            current["recovered"] = delta_data["recovered"]
                        if "tested" in delta_data.keys():
                            current["tested"] = delta_data["tested"]
                    total = {
                        "total_confirm": 0,
                        "total_recovered": 0,
                        "total_death": 0,
                        "total_tested": 0,
                        "total_vaccinated1": 0,
                        "total_vaccinated2": 0,
                    }
                    if "total" in date_data.keys():
                        total_data = date_data["total"]
                        if "confirmed" in total_data.keys():
                            total["total_confirm"] = total_data["confirmed"]
                        if "recovered" in total_data.keys():
                            total["total_recovered"] = total_data["recovered"]
                        if "deceased" in total_data.keys():
                            total["total_death"] = total_data["deceased"]
                        if "tested" in total_data.keys():
                            total["total_tested"] = total_data["tested"]
                        if "vaccinated1" in total_data.keys():
                            total["total_vaccinated1"] = total_data["vaccinated1"]
                        if "vaccinated2" in total_data.keys():
                            total["total_vaccinated2"] = total_data["vaccinated2"]
                    dates_data_json[d] = {
                        "confirm": current["confirm"],
                        "recovered": current["recovered"],
                        "deaths": current["deaths"],
                        "tested": current["tested"],
                        "active": current["confirm"] - (current["recovered"] + current["deaths"]),
                        "total_confirm": total["total_confirm"],
                        "total_recovered": total["total_recovered"],
                        "total_death": total["total_death"],
                        "total_tested": total["total_tested"],
                        "total_active": total["total_confirm"] - (total["total_recovered"] + total["total_death"]),
                        "total_vaccinated1": total["total_vaccinated1"],
                        "total_vaccinated2": total["total_vaccinated2"]
                    }
                    
            today = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%dT%H:%M:%S%z')
            state_covid_data = StateCovidData(
                state_code=state,
                state_name=state_name,
                dates_data=dates_data_json,
                note="",
                last_update=today,
                population=0
            )
            state_covid_data.save()




def get_daily_data():
    print("collecting data from indian gov. server.....")
    data = StateCovidData.objects.all().exists()
    if(not data):
        collect_previous_data()
    data = requests.get("https://data.covid19india.org/v4/min/data.min.json")
    min_date = date.today() - timedelta(days=200)
    json_data = data.json()
    state_details = getStates()
    for state_code in json_data.keys():
        state_data = json_data[state_code]
        if state_code != 'UN':
            state_code = state_code if state_code != 'TT' else "IN"
            state_name = state_details[state_code]
            state_data_object = StateCovidData.objects.filter(state_name=state_name, state_code=state_code).first()
            # print(state_data_object)
            dates_data = {}
            if state_data_object is not None:
                dates_data = state_data_object.dates_data
                del_dates = []
                for d in dates_data.keys():
                    if d < str(min_date):
                        del_dates.append(d)
                for d in del_dates:
                    del dates_data[d]
            # print(dates_data)
            # print(state_data.keys())
            date_data = state_data
            current = {
                "confirm": 0,
                "recovered": 0,
                "deaths": 0,
                "tested": 0
            }
            if "delta" in date_data.keys():
                delta_data = date_data["delta"]
                if "confirmed" in delta_data.keys():
                    current["confirm"] = delta_data["confirmed"]
                if "deceased" in delta_data.keys():
                    current["deaths"] = delta_data["deceased"]
                if "recovered" in delta_data.keys():
                    current["recovered"] = delta_data["recovered"]
                if "tested" in delta_data.keys():
                    current["tested"] = delta_data["tested"]
            total = {
                "total_confirm": 0,
                "total_recovered": 0,
                "total_death": 0,
                "total_tested": 0,
                "total_vaccinated1": 0,
                "total_vaccinated2": 0,
            }
            if "total" in date_data.keys():
                total_data = date_data["total"]
                if "confirmed" in total_data.keys():
                    total["total_confirm"] = total_data["confirmed"]
                if "recovered" in total_data.keys():
                    total["total_recovered"] = total_data["recovered"]
                if "deceased" in total_data.keys():
                    total["total_death"] = total_data["deceased"]
                if "tested" in total_data.keys():
                    total["total_tested"] = total_data["tested"]
                if "vaccinated1" in total_data.keys():
                    total["total_vaccinated1"] = total_data["vaccinated1"]
                if "vaccinated2" in total_data.keys():
                    total["total_vaccinated2"] = total_data["vaccinated2"]
            meta_data_json = {
                "date": "",
                "last_update": "",
                "note": "",
                "population": 0
            }
            if "meta" in date_data.keys():
                meta_data = date_data["meta"]
                if "date" in meta_data.keys():
                    meta_data_json["date"] = meta_data["date"]
                if "last_updated" in meta_data.keys():
                    meta_data_json["last_update"] = meta_data["last_updated"]
                if "population" in meta_data.keys():
                    meta_data_json["population"] = meta_data["population"]
                if "notes" in meta_data.keys():
                    meta_data_json["note"] = meta_data["notes"]
            # print(meta_data_json)
            dates_data[meta_data_json["date"]] = {
                "confirm": current["confirm"],
                "recovered": current["recovered"],
                "deaths": current["deaths"],
                "tested": current["tested"],
                "active": current["confirm"] - (current["recovered"] + current["deaths"]),
                "total_confirm": total["total_confirm"],
                "total_recovered": total["total_recovered"],
                "total_death": total["total_death"],
                "total_tested": total["total_tested"],
                "total_active": total["total_confirm"] - (total["total_recovered"] + total["total_death"]),
                "total_vaccinated1": total["total_vaccinated1"],
                "total_vaccinated2": total["total_vaccinated2"]
            }

            state_covid_data = StateCovidData(
                state_code=state_code,
                state_name=state_name,
                dates_data=dates_data,
                note=meta_data_json["note"],
                last_update=meta_data_json["last_update"],
                population=meta_data_json["population"]
            )
            state_covid_data_old = StateCovidData.objects.filter(state_code=state_code)
            for old_data in state_covid_data_old:
                old_data.delete()
            state_covid_data.save()


