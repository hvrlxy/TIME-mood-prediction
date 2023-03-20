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
        try:
            location_df = location_df[['LOCATION_TIME', 'LONG', 'LAT', 'ALTITUDE']]
        except Exception as e:
            # create an empty df with columns LOCATION_TIME, LONG, LAT and ALTITUDE and 1440 rows
            empty_df = pd.DataFrame(columns=['LOCATION_TIME', 'LONG', 'LAT', 'ALTITUDE'], index=range(1440))
            # impute the minutes into the LOCATION_TIME column
            empty_df['LOCATION_TIME'] = pd.date_range(start='00:00', end='23:59', freq='1min')
            # turn the LOCATION_TIME column back into a string with format YYYY-MM-DD HH:MM:SS
            empty_df['LOCATION_TIME'] = empty_df['LOCATION_TIME'].dt.strftime('%Y-%m-%d %H:%M:%S')
            # create a folder inside the data/clean folder named location
            if not os.path.exists(self.DATA_CLEAN_DIR + 'location'):
                os.makedirs(self.DATA_CLEAN_DIR + 'location')
            #create the participant folder follows by the date folder inside the location folder, if it doesn't exist
            if not os.path.exists(self.DATA_CLEAN_DIR + f'location/{participantID}/{date}'):
                os.makedirs(self.DATA_CLEAN_DIR + f'location/{participantID}/{date}')
            # save the location_df as a csv file inside the location/participantID/date folder
            location_df.to_csv(self.DATA_CLEAN_DIR + f'location/{participantID}/{date}/location_{date}.csv', index=False)
            # return the empty df
            return empty_df
        
        # turn the LOCATION_TIME column into a datetime object
        location_df['LOCATION_TIME'] = pd.to_datetime(location_df['LOCATION_TIME'])
        # reset the second and microsecond to 0
        location_df['LOCATION_TIME'] = location_df['LOCATION_TIME'].dt.floor('min')
        #print duplicated LOCATION_TIME
        # print(location_df[location_df.duplicated(subset=['LOCATION_TIME'], keep=False)])
        # delete the duplicate rows
        location_df = location_df.drop_duplicates(subset=['LOCATION_TIME'])
        # impute missing rows (interval of 1 minute)
        location_df = self.impute_missing_rows(location_df)

        # turn the LOCATION_TIME column back into a string with format YYYY-MM-DD HH:MM:SS
        location_df['LOCATION_TIME'] = location_df['LOCATION_TIME'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # create a folder inside the data/clean folder named location
        if not os.path.exists(self.DATA_CLEAN_DIR + 'location'):
            os.makedirs(self.DATA_CLEAN_DIR + 'location')
        #create the participant folder follows by the date folder inside the location folder, if it doesn't exist
        if not os.path.exists(self.DATA_CLEAN_DIR + f'location/{participantID}/{date}'):
            os.makedirs(self.DATA_CLEAN_DIR + f'location/{participantID}/{date}')
        # save the location_df as a csv file inside the location/participantID/date folder
        location_df.to_csv(self.DATA_CLEAN_DIR + f'location/{participantID}/{date}/location_{date}.csv', index=False)
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

    def process_location_participant(self, participantID):
        # get the study_dates.json file as a dict
        with open(self.DATA_CLEAN_DIR + f'study/study_dates.json') as json_file:
            # get the dates of the participant
            dates = json.load(json_file)[participantID]
            #get the start date of the participant
            start_date = dates[0]
            # get the end date of the participant
            end_date = dates[1]
            ##turn the start date and end date into datetime objects
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            #loop through the dates between the start date and the end date
            for date in pd.date_range(start_date, end_date):
                # turn the date into a string with format YYYY-MM-DD
                date = date.strftime('%Y-%m-%d')
                # get the location at the date
                self.get_location_at_date(participantID, date)

obj = Location()
# print(
obj.process_location_participant('afflictedrevenueepilepsy')
# )
    