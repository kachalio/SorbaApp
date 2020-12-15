import datetime
import logging, os, datetime, requests, json

import azure.functions as func

# pylint: disable=unsubscriptable-object
def main(mytimer: func.TimerRequest, outputBlob: func.Out[str]):
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    logging.info(f"Blob trigger executed!")

    # Setting variables
    rain_accumulation_query_url = os.environ["RAIN_ACCUMULATION_QUERY_URL"]
    params = {
        'start_date_hours_previous' : os.environ["OW_START_DATE_HOURS_PREVIOUS"],
        'end_date_hours_ago' : os.environ["OW_END_DATE_HOURS_AGO"],
        'LAT' : os.environ["OW_LAT"],
        'LNG' : os.environ["OW_LNG"]
    }

    r = requests.get(rain_accumulation_query_url, params=params)
    
    if r.status_code == 200 and json.loads(r.text)['rain_accumulation'] > 0:
        output = r.text
        outputBlob.set(output)
        logging.info("Blob created.")
    else:
        logging.info("Blob not created")
        logging.info("Error: %s", r.text)