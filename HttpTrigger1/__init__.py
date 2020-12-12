import logging, datetime, os, json

import azure.functions as func

from .rainAlerts import OpenWeather as OpenWeather


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')


    # getting parameters
    lat = req.params.get('lat', os.environ["LAT"])
    lon = req.params.get('lon', os.environ["LNG"])
    end_date_hours_ago = int(req.params.get('end_date_hours_ago', os.environ["END_DATE_HOURS_AGO"]))
    start_date_hours_previous = int(req.params.get('start_date_hours_previous', os.environ["START_DATE_HOURS_PREVIOUS"]))
    end_date = (datetime.datetime.now() - datetime.timedelta(hours=int(end_date_hours_ago))).replace(microsecond=0)
    start_date = (end_date - datetime.timedelta(hours=int(start_date_hours_previous))).replace(microsecond=0)
    return_data = None

    # Creating an open weather object
    ow = OpenWeather(os.environ["API_KEY"])

    historical_weather_data = ow.onecall_historical_between_dates(lat, lon,start_date, end_date)

    if historical_weather_data['status_code'] != 200:
        return func.HttpResponse(historical_weather_data['text'],status_code=historical_weather_data['status_code'])
    else:
        rain_accumulation = ow.get_rain_accumulation(historical_weather_data['hourly'])

        return_data = {'text' : {'start_date' : start_date.isoformat(), 'end_date' : end_date.isoformat(), 'rain_accumulation' : rain_accumulation}, 'status_code' : 200 }



    # data = None
    # if not name:
    #     try:
    #         req_body = req.get_json()
    #     except ValueError:
    #         pass
    #     else:
    #         name = req_body.get('name')

    # data = rainAlerts.main_function(end_date, start_date, lat, lon)

    if return_data:
        return func.HttpResponse(json.dumps(return_data['text']),status_code=return_data['status_code'])
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
