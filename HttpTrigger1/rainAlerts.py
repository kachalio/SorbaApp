### I'm using the Openweather API free version.
### 2020
### Zack Kachaylo


import requests, os, datetime, json

import azure.functions as func


class OpenWeather:

    def __init__(self, api_key, base_url = "https://api.openweathermap.org/data/2.5/"):
        self.api_key = api_key
        self.base_url = base_url

    
    def onecall_historical(self, lat, lon, end_date, units="imperial"):

        url = "%s%s" % (self.base_url, "onecall/timemachine")
        params = {
            'units' : units,
            'appid' : self.api_key,
            'lat' : lat,
            'lon' : lon,
            'dt' : str(end_date.timestamp()).split(".")[0]
        }
        
        return requests.request("GET", url, params=params, data=None, headers=None)
    
    def one_call_current(self):
        pass

    def filter_weather_data_dates(self, all_weather_data_list, start_date, end_date):
        all_hourly_data_filtered = []

        for record in all_weather_data_list:
            # Getting the earliest date from weather dataset
            record_date = datetime.datetime.fromtimestamp(record['dt'])
            
            # Loop through and check if hourly api data is greater than or equal to the start date then add to all hourly data
            if record_date >= start_date and record_date <= end_date:
                all_hourly_data_filtered.append(record)
        
        # create new data with api call and all hourly data
        return_data = {'hourly':[], 'status_code':200}
        # sorting hourly data list by time stamp before returning
        return_data['hourly'] = sorted(all_hourly_data_filtered, key = lambda i: i['dt'])
        return return_data


    def onecall_historical_between_dates(self, lat, lon, start_date, end_date, original_end_date=None, all_hourly_data=[], units="imperial"):
        
        #setting variable to preserve original end date
        if original_end_date is None:
            original_end_date = end_date

        # Making API call 
        response_weather_data = self.onecall_historical(lat, lon, end_date)

        if response_weather_data.status_code != 200:
            return_weather_data_dict = {'text':response_weather_data.text, 'status_code' : response_weather_data.status_code}
            return return_weather_data_dict

        # Extracting hourly weather data from API response
        hourly_weather_data_list = json.loads(response_weather_data.text)['hourly']

        # Getting the earliest date from weather dataset
        hourly_weather_data_earliest_date = datetime.datetime.fromtimestamp(hourly_weather_data_list[0]['dt'])

        # Decreasing the earliest date by one hour
        new_end_date = (hourly_weather_data_earliest_date - datetime.timedelta(hours=1)).replace(microsecond=0)

        # Checking to see if the earliest date in the weather data list is greater than the start date
        if hourly_weather_data_earliest_date > start_date:
            # adding current hourly weather data list into all hourly data list
            all_hourly_data = hourly_weather_data_list + all_hourly_data
            # calling this function again to query the API with a new, earlier date range
            return self.onecall_historical_between_dates(lat, lon, start_date, new_end_date, original_end_date, all_hourly_data, units=units)
        # iterate hourly weather data to add to filter results to specified time range
        else:
            
            # Combine all weather data with most recent weather list
            all_hourly_data.extend(hourly_weather_data_list)

            date_filtered_weather_data = self.filter_weather_data_dates(all_hourly_data, start_date, original_end_date)

            # return return_data
            return date_filtered_weather_data

    
    def mm_to_inch(self, mm):
        # Simple function to convert mm to inches as the API doesn't seem to want to do that.
        inches = mm * 0.0393701
        return inches

    def get_rain_accumulation(self, weather_list):
        accumulated_rainfall = 0    
        for record in weather_list:
            # Checking if the hour of weather data contains information for rain
            if "rain" in record:
                rain_accumulation_in_inches = self.mm_to_inch(record['rain']['1h'])
                accumulated_rainfall += rain_accumulation_in_inches
        
        return accumulated_rainfall