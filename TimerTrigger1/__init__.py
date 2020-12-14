import datetime
import logging

import azure.functions as func

from azure.storage.blob import BlobServiceClient, BlobClient
import os, requests, json

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    # Setting variables
    storage_connection_string = os.environ["STORAGE_CONNECTION_STRING"]
    container_name = os.environ["RAIN_HISTORY_CONTAINER_NAME"]
    rain_accumulation_query_url = os.environ["RAIN_ACCUMULATION_QUERY_URL"]
    params = {
        'start_date_hours_previous' : None,
        'end_date_hours_ago' : None,
        'LAT' : None,
        'LNG' : None
    }

    r = requests.get(rain_accumulation_query_url, params=params)

    
    if r.status_code == 200 and json.loads(r.text)['rain_accumulation'] > 0:
        blob = BlobClient.from_connection_string(conn_str=storage_connection_string, container_name=container_name, blob_name="rain_query_%s.json" % (datetime.datetime.now()))
        blob.upload_blob(r.text)
    
    func.HttpResponse(r.text, status_code=r.status_code)

    
