import os
import traceback
import pandas as pd
import warnings
from logger import Logger
from participant import Participant
from globals import *
import json

warnings.filterwarnings("ignore")

class Location:
    def __init__(self):
        self.logger = Logger().getLog('EMA')
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        self.DATA_RAW_DIR = self.ROOT_DIR + '/data/raw/'
        self.DATA_FILTER_DIR = self.ROOT_DIR + '/data/filtered/'
        self.DATA_CLEAN_DIR = self.ROOT_DIR + '/data/clean/'
        self.REPORTS_DIR = self.ROOT_DIR + '/reports/'
        self.participant = Participant()
    
    def get_location_at_date(self, participantID, date):
        # get the csv file as a df inside the raw folder/participantID/date
        location_df = pd.read_csv(self.DATA_RAW_DIR + f'intermediate_file/{participantID}@timestudy_com/{date}/phone_GPS_clean_{date}.csv')
        # only get the LOCATION_TIME, LONG, LAT and ALTITUDE columns
        location_df = location_df[['LOCATION_TIME', 'LONG', 'LAT', 'ALTITUDE']]
        # turn the LOCATION_TIME column into a datetime object
        location_df['LOCATION_TIME'] = pd.to_datetime(location_df['LOCATION_TIME'])
        # reset the second and microsecond to 0
        location_df['LOCATION_TIME'] = location_df['LOCATION_TIME'].dt.floor('min')
        #print duplicated LOCATION_TIME
        print(location_df[location_df.duplicated(subset=['LOCATION_TIME'], keep=False)])
        # delete the duplicate rows
        location_df = location_df.drop_duplicates(subset=['LOCATION_TIME'])
        # impute missing rows (interval of 1 minute)
        location_df = self.impute_missing_rows(location_df)

        # turn the LOCATION_TIME column back into a string with format YYYY-MM-DD HH:MM:SS
        location_df['LOCATION_TIME'] = location_df['LOCATION_TIME'].dt.strftime('%Y-%m-%d %H:%M:%S')
        return location_df

    def impute_missing_rows(self, location_df):
        # get the column as a list
        date_list = location_df['LOCATION_TIME'].tolist()
        current_date = date_list[0]
        current_index = 1
        # loop through the date_list
        while (current_index < len(date_list)):
            # if the current date is more than 1 minute away from the previous date, add the missing dates
            # to the location_df, with other columns filled with NaN
            if (date_list[current_index] - current_date).seconds > 60:
                for i in range(1, (date_list[current_index] - current_date).seconds // 60):
                    location_df = location_df.append({'LOCATION_TIME': current_date + pd.Timedelta(minutes=i), 'LONG': float('nan'), 'LAT': float('nan'), 'ALTITUDE': float('nan')}, ignore_index=True)
            current_date = date_list[current_index]
            current_index += 1
        # sort the location_df by the LOCATION_TIME
        location_df = location_df.sort_values(by=['LOCATION_TIME'])
        return location_df

obj = Location()
# print(
obj.get_location_at_date('afflictedrevenueepilepsy', '2021-06-05')
# )
    