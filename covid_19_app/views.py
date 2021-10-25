from django.shortcuts import render, HttpResponse
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
import re
from .utils import *
import json
import uuid
import os, base64
import dialogflow

from google.cloud import dialogflow_v2beta1 as dialogflow_kb
from django.conf import settings



@api_view(["GET"])
def home(request):
    return Response({"message":"home"},status=200)

@api_view(['GET'])
def total_data_all_states(request):  
    all_data = StateCovidData.objects.all()
    result={}
    country_data={}
    states_data=[]
    for data in all_data:  
        dates_data = data.dates_data
        lastest_date = max(date for date in dates_data.keys())
        last_data = dates_data[lastest_date]
        state_data={
            "state_code":data.state_code,
            "state_name":data.state_name,
            "population":data.population,
            "last_update":data.last_update,
            "note":data.note,
            "confirm": last_data["confirm"],
            "recovered":last_data["recovered"],
            "deaths":last_data["deaths"],
            "tested":last_data["tested"],
            "active": last_data["active"],
            "total_confirm":last_data["total_confirm"],
            "total_recovered":last_data["total_recovered"],
            "total_death":last_data["total_death"],
            "total_tested":last_data["total_tested"],
            "total_active":last_data["total_active"],
            "total_vaccinated1":last_data["total_vaccinated1"],
            "total_vaccinated2":last_data["total_vaccinated2"],
        }
        if data.state_code != "IN":
            states_data.append(state_data)
        else:
            country_data = state_data
        
    states_data = sorted(states_data, key = lambda i: i['total_confirm'],reverse=True)
    result = {
            "country_data":country_data,
            "states_data":states_data
        }
    return Response(result,status=200)

@api_view(['GET'])
def total_data_states(request,code):  
    state_data = StateCovidData.objects.filter(state_code=code).first()
    country_data = StateCovidData.objects.filter(state_code="IN").first()
    state_json={}
    country_json={}
    if state_data is not None:
        for data in [state_data,country_data]:
            dates_data = data.dates_data
            lastest_date = max(date for date in dates_data.keys())
            last_data = dates_data[lastest_date]
            json_data={
                "state_code":data.state_code,
                "state_name":data.state_name,
                "population":data.population,
                "last_update":data.last_update,
                "note":data.note,
                "confirm": last_data["confirm"],
                "recovered":last_data["recovered"],
                "deaths":last_data["deaths"],
                "tested":last_data["tested"],
                "active": last_data["active"],
                "total_confirm":last_data["total_confirm"],
                "total_recovered":last_data["total_recovered"],
                "total_death":last_data["total_death"],
                "total_tested":last_data["total_tested"],
                "total_active":last_data["total_active"],
                "total_vaccinated1":last_data["total_vaccinated1"],
                "total_vaccinated2":last_data["total_vaccinated2"],
            }
            if data.state_code != "IN":
                state_json = json_data
            else:
                if code=="IN":
                    state_json=json_data
                country_json = json_data

        result = {
            "country_data":state_json,
            "state_data":country_json
        }
        return Response(result,status=200)
    else:
        return Response({"result":"wrong state code"},status=400)




@api_view(['post'])
def statewise_timeseries_data(request): 
    data = request.data
    date_regex = "^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$"
    state_code = data.get("state_code","")
    start_date = data.get("start_date","")
    end_date = data.get("end_date","")
    if re.search(date_regex, start_date) and re.search(date_regex, end_date) and re.search("^[A-Z]{2}$",state_code):
        if(start_date<end_date):
            
            result_dates_data=[]
            state_data = StateCovidData.objects.filter(state_code=state_code).first()
            if state_data is not None:
                dates_data = state_data.dates_data
                for date in dates_data.keys():
                    print(date)
                    if date>=start_date and date<=end_date:
                        d = dates_data[date]
                        res = {
                            "date":date,
                            "total_confirm":d["total_confirm"],
                            "total_recovered":d["total_recovered"],
                            "total_death":d["total_death"],
                            "total_tested":d["total_tested"],
                            "total_active":d["total_active"],
                            "total_vaccinated1":d["total_vaccinated1"],
                            "total_vaccinated2":d["total_vaccinated2"],
                            "confirm":d["confirm"],
                            "recovered":d["recovered"],
                            "deaths":d["deaths"],
                            "tested":d["tested"],
                            "active":d["active"],
                        }
                        result_dates_data.append(res)
                result = {
                    "state_code":state_code,
                    "start_date":start_date,
                    "end_date":end_date,
                    "state_name":state_data.state_name,
                    "note":state_data.note,
                    "population":state_data.population,
                    "last_update":state_data.last_update,
                    "data":result_dates_data

                }
                return Response(result,status=200)
    
    return Response({"message":"invalid"},status=400)

@api_view(["GET"])
def get_data(request):
    get_daily_data()
    return Response({"message":"done"},status=200)

@api_view(['POST'])
def get_charbot_data(request):
    data = request.data
    print(data)
    sessionID = data.get('responseId')
    result = data.get("queryResult")
    intent = result.get("intent").get('displayName')
    query_text = result.get("queryText")
    parameters = result.get("parameters")
    if intent=="search_state":
        state_name = parameters.get("geo-state")[0]
        webhookresponse = get_data_states(state_name)
        webhookresponse = "*********\n" + " State :" + str(webhookresponse['state']) + \
                                    "\n" + " Confirmed cases : " + str(
                    webhookresponse['confirm']) + "\n" + " Death cases : " + str(webhookresponse['deaths']) + \
                                    "\n" + " Active cases : " + str(
                    webhookresponse['active']) + "\n" + " Recovered cases : " + str(
                    webhookresponse['recovered']) + "\n*********"
        
        result_json={
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhookresponse
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            "main menu,exit"
                            # "We have sent the detailed report of {} Covid-19 to your given mail address.Do you have any other Query?".format(cust_country)
                        ]

                    }
                }  
            ]
        }
        return Response(result_json,status=200)
    elif intent=="search_country":
        country_name = parameters.get("geo-country")[0]
        if(country_name=="United States"):
            country_name = "USA"
        required_data, deaths_data, testsdone_data = get_data_country(country_name)
        
        webhookresponse = "***Covid Report*** \n\n" + " New cases :" + str(required_data.get('new')) + \
                        "\n" + " Active cases : " + str(
            required_data.get('active')) + "\n" + " Critical cases : " + str(required_data.get('critical')) + \
                        "\n" + " Recovered cases : " + str(
            required_data.get('recovered')) + "\n" + " Total cases : " + str(required_data.get('total')) + \
                        "\n" + " Total Deaths : " + str(deaths_data.get('total')) + "\n" + " New Deaths : " + str(
            deaths_data.get('new')) + \
                        "\n" + " Total Test Done : " + str(deaths_data.get('total')) + "\n\n*******END********* \n "
        print(webhookresponse)
        result =  {

            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhookresponse
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            "main menu,exit"
                            # "We have sent the detailed report of {} Covid-19 to your given mail address.Do you have any other Query?".format(cust_country)
                        ]

                    }
                }
            ]
        }
        return Response(result,status=200)
    elif intent=="total_cases":
        fulfillmentText = get_total_data()

        webhookresponse = "***World wide Report*** \n\n" + " Confirmed cases :" + str(
            fulfillmentText.get('confirmed')) + \
                          "\n" + " Deaths cases : " + str(
            fulfillmentText.get('deaths')) + "\n" + " Recovered cases : " + str(fulfillmentText.get('recovered')) + \
                          "\n" + " Active cases : " + str(
            fulfillmentText.get('active')) + "\n" + " Fatality Rate : " + str(
            fulfillmentText.get('fatality_rate') * 100) + "%" + \
                          "\n" + " Last updated : " + str(
            fulfillmentText.get('last_update')) + "\n\n*******END********* \n "
        print(webhookresponse)
        result_json ={

            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            webhookresponse
                        ]

                    }
                },
                {
                    "text": {
                        "text": [
                            "main menu,exit"
                            # "We have sent the detailed report of {} Covid-19 to your given mail address.Do you have any other Query?".format(cust_country)
                        ]

                    }
                }
            ]
        }
        return Response(result_json,status=200)

    result_json = {
        "text":"ok"
    }
    return Response(result_json,status=200)

def get_data_states(name):  
    data = StateCovidData.objects.filter(state_name=name).first()
    state_json={}
    dates_data = data.dates_data
    lastest_date = max(date for date in dates_data.keys())
    last_data = dates_data[lastest_date]
    state_json={
        "state_code":data.state_code,
        "state":data.state_name,
        "confirm":last_data["total_confirm"],
        "recovered":last_data["total_recovered"],
        "deaths":last_data["total_death"],
        "active":last_data["total_active"],
    }
            
    return state_json
        

def get_data_country(name):  
    
    url = "https://covid-193.p.rapidapi.com/statistics"

    querystring = {"country":name}

    headers = {
        'x-rapidapi-host': "covid-193.p.rapidapi.com",
        'x-rapidapi-key': "55b6689c46msh94bae1227dbe83dp1b4268jsnb7b812a6f9fd"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)
    # print(result)
    result=result["response"][0]
    return result.get('cases') , result.get('deaths'),result.get('tests')


def get_total_data():
    url = "https://covid-19-statistics.p.rapidapi.com/reports/total"

    headers = {
        'x-rapidapi-host': "covid-19-statistics.p.rapidapi.com",
        'x-rapidapi-key': "55b6689c46msh94bae1227dbe83dp1b4268jsnb7b812a6f9fd"
        }

    response = requests.request("GET", url, headers=headers)

    # print(response.text)
    result = json.loads(response.text)
    return result.get('data')

@api_view(["POST"])
def chat_bot(request):
    # session_id = str(uuid.uuid5())
    GOOGLE_AUTHENTICATION_FILE_NAME = settings.GCS_CREDENTIALS_FILE_PATH
    current_directory = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(current_directory, GOOGLE_AUTHENTICATION_FILE_NAME)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
    GOOGLE_PROJECT_ID = settings.GS_PROJECT_ID
    GOOGLE_KNOWLEDGE_ID = settings.GS_KNOWLEDGE_ID
    session_id = "1234567891"
    context_short_name = "does_not_matter"
    input_text = request.data.get("input","")
    # print(input_text)
    context_name = "projects/" + GOOGLE_PROJECT_ID + "/agent/sessions/" + session_id + "/contexts/" + \
               context_short_name.lower()
    parameters = dialogflow.types.struct_pb2.Struct()
    context_1 = dialogflow.types.context_pb2.Context(
        name=context_name,
        lifespan_count=2,
        parameters=parameters
    )
    query_params_1 = {"contexts": [context_1]}
    language_code = 'en'
    response = detect_intent_knowledge(GOOGLE_PROJECT_ID,session_id,language_code,GOOGLE_KNOWLEDGE_ID,input_text)
    # print('response is: ',response)
    print(len(response))
    output_text = ""
    quick_reply = []
    if len(response)==2:
        quick_reply = str(response[1].text.text[0]).split(',')
    output_text = response[0].text.text[0]
    # print(quick_reply)
    # print(output_text)
    
    return Response({"response":output_text,"quick reply":quick_reply},status=200)


## Function to call Dialogflow detectintent API endpoint

def detect_intent_knowledge(project_id, session_id, language_code, knowledge_base_id, text):
   
    session_client = dialogflow_kb.SessionsClient()

    session_path = session_client.session_path(project_id, session_id)
    print("Session path: {}\n".format(session_path))

    text_input = dialogflow_kb.TextInput(text=text, language_code=language_code)

    query_input = dialogflow_kb.QueryInput(text=text_input)

    knowledge_base_path = dialogflow_kb.KnowledgeBasesClient.knowledge_base_path(
        project_id, knowledge_base_id
    )

    query_params = dialogflow_kb.QueryParameters(
        knowledge_base_names=[knowledge_base_path]
    )

    request = dialogflow_kb.DetectIntentRequest(
        session=session_path, query_input=query_input, query_params=query_params
    )
    response = session_client.detect_intent(request=request)
    # for testing
    # print("=" * 20)
    # print("Query text: {}".format(response.query_result.query_text))
    # print(
    #     "Detected intent: {} (confidence: {})\n".format(
    #         response.query_result.intent.display_name,
    #         response.query_result.intent_detection_confidence,
    #     )
    # )
    # print("Fulfillment text: {}\n".format(response.query_result.fulfillment_text))
    # print("Knowledge results:")
    # knowledge_answers = response.query_result.knowledge_answers
    # print(response)
    # for answers in knowledge_answers.answers:
    #     print(" - Answer: {}".format(answers.answer))
    #     print(" - Confidence: {}".format(answers.match_confidence))

    return response.query_result.fulfillment_messages


