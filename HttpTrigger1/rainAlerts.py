### I'm using the Openweather API free version.
### 2020
### Zack Kachaylo


import requests, os, datetime, json

import azure.functions as func

def mm_to_inch(mm):
    # Simple function to convert mm to inches as the API doesn't seem to want to do that.
    inches = mm * 0.0393701
    return inches

class OpenWeather:

    def __init__(self, api_key, base_url = "https://api.openweathermap.org/data/2.5/"):
        self.api_key = api_key
        self.base_url = base_url
    

    def one_call_historical(self, lat, lon, start_date, end_date, units="imperial"):

        url = "%s%s" % (self.base_url, "onecall/timemachine")
        querystring = {
            'units' : units,
            'appid' : self.api_key,
            'lat' : lat,
            'lon' : lon,
            'dt' : str(end_date.timestamp()).split(".")[0]
        }
        
        return self.make_request(url, querystring)
    
    def make_request(self, url, params, data=None, headers=None):
        import requests
        return requests.request("GET", url, params=params, data=None, headers=headers)

    def historical_between_dates(self, lat, lon, start_date, end_date, original_end_date, all_hourly_data=[], units="imperial"):

        #setting variable to preserve original end date
        original_end_date = original_end_date

        # Making API call 
        data = self.one_call_historical(lat, lon, start_date, end_date)

        if data.status_code != 200:
            response_data = {'text':data.text, 'status_code' : data.status_code}
            return response_data

        # Extracting hourly weather data from API response
        hourly_data = json.loads(data.text)['hourly']

        # Getting the earliest date from weather dataset
        hourly_data_earliest_date = datetime.datetime.fromtimestamp(hourly_data[0]['dt'])

        # Decreasing the earliest date by one hour
        new_end_date = (hourly_data_earliest_date - datetime.timedelta(hours=1)).replace(microsecond=0)

        if hourly_data_earliest_date > start_date:
            # Recalling the API call with the earliest date decremented by one hour to pull next day dataset
            all_hourly_data = hourly_data + all_hourly_data
            return self.historical_between_dates(lat, lon, start_date, new_end_date, original_end_date, all_hourly_data, units=units)
        else:
            # loop through hourly data to add to export specific date range
            all_hourly_data.extend(hourly_data)

            all_hourly_data_filtered = []

            for record in all_hourly_data:
                # Getting the earliest date from weather dataset
                record_date = datetime.datetime.fromtimestamp(record['dt'])
                
                # Loop through and check if hourly api data is greater than or equal to the start date then add to all hourly data
                if record_date >= start_date and record_date <= original_end_date:
                    all_hourly_data_filtered.append(record)
            
            # create new data with api call and all hourly data
            return_data = json.loads(data.text)
            # sorting hourly data list by time stamp before returning
            return_data['hourly'] = sorted(all_hourly_data_filtered, key = lambda i: i['dt'])
            return_data['status_code'] = data.status_code
            return return_data

def get_rain_accumulation(hourly_data):
    
    accumulated_rainfall = 0    
    for record in hourly_data:
        # Checking if the hour of weather data contains information for rain
        if "rain" in record:
            rain_accumulation_in_inches = mm_to_inch(record['rain']['1h'])
            accumulated_rainfall += rain_accumulation_in_inches
    
    return accumulated_rainfall
 

def main_function(end_date, start_date, lat, lon):
    
    # Variables
    end_date = end_date
    start_date = start_date
    lat = lat
    lon = lon

    ow = OpenWeather(os.environ.get('API_KEY'))
    # data = ow.one_call_historical(lat, lon, start_date, end_date)

    data = ow.historical_between_dates(lat, lon, start_date, end_date, end_date)

    if data['status_code'] != 200:
        return data

    rain_accumulation = get_rain_accumulation(data['hourly'])

    json_start_date = start_date.isoformat()
    json_end_date = end_date.isoformat()

    if rain_accumulation > 0:
        json_start_date = datetime.datetime.fromtimestamp(data['hourly'][0]['dt']).isoformat()
        json_end_date = datetime.datetime.fromtimestamp(data['hourly'][len(data['hourly'])-1]['dt']).isoformat()


    
    # print("Accumulated Rainfall between %s and %s is %s inches" % (start_time, end_time,  round(accumulated_rainfall,2)))

    return {'text' :{'start_date' : json_start_date, 'end_date' : json_end_date, 'rain_accumulation' : round(rain_accumulation, 2)}, 'status_code' : data['status_code']}


# if __name__ == "__main__":
#     print(main_function())
