import logging, datetime, os

import azure.functions as func

from . import rainAlerts

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name', "Zack")

    # getting parameters
    end_date_hours_ago = req.params.get('end_date_hours_ago', int(os.environ.get('END_DATE_HOURS_AGO')))
    start_date_hours_previous = req.params.get('start_date_hours_previous', int(os.environ.get('START_DATE_HOURS_PREVIOUS')))
    lat = req.params.get('lat', os.environ.get('LAT'))
    lon = req.params.get('lon', os.environ.get('LNG'))

    # using date hours ago parameters to create date objects
    end_date = (datetime.datetime.now() - datetime.timedelta(hours=int(end_date_hours_ago))).replace(microsecond=0)
    start_date = (end_date - datetime.timedelta(hours=int(start_date_hours_previous))).replace(microsecond=0)

    data = None
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    data = rainAlerts.main_function(end_date, start_date, lat, lon)

    if data:
        return func.HttpResponse(f"{data}")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
