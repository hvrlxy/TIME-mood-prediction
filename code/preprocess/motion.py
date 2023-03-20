import os
import traceback
import pandas as pd
import numpy as np
import warnings
from logger import Logger
from participant import Participant
import json

warnings.filterwarnings("ignore")

class Motion:
    def __init__(self):
        self.logger = Logger().getLog('motion')
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        self.DATA_RAW_DIR = self.ROOT_DIR + '/data/raw/'
        self.DATA_FILTER_DIR = self.ROOT_DIR + '/data/filtered/'
        self.DATA_CLEAN_DIR = self.ROOT_DIR + '/data/clean/'
        self.REPORTS_DIR = self.ROOT_DIR + '/reports/'
        self.participant = Participant()

    def get_motion_at_date(self, participantID, date):
        try:
            # get the csv file as a df inside the raw folder/participantID/date
            motion_df = pd.read_csv(self.DATA_RAW_DIR + f'intermediate_file/{participantID}@timestudy_com/{date}/phone_detected_activity_clean_{date}.csv')
                                # names=['LOG_TIME','IN_VEHICLE','ON_BIKE','ON_FOOT','RUNNING','STILL','TILTING','WALKING','UNKNOWN']
        except Exception as e:
            # create an empty df with columns LOG_TIME, LONG, LAT and ALTITUDE and 1440 rows
            empty_df = pd.DataFrame(columns=['LOG_TIME','IN_VEHICLE','ON_BIKE','ON_FOOT','RUNNING','STILL','TILTING','WALKING','UNKNOWN']
                                    , index=range(1440))
            # impute the minutes into the LOG_TIME column
            empty_df['LOG_TIME'] = pd.date_range(start='00:00', end='23:59', freq='1min')
            # turn the LOG_TIME column back into a string with format YYYY-MM-DD HH:MM:SS
            empty_df['LOG_TIME'] = empty_df['LOG_TIME'].dt.strftime('%Y-%m-%d %H:%M:%S')
            # create a folder inside the data/clean folder named location
            if not os.path.exists(self.DATA_CLEAN_DIR + 'location'):
                os.makedirs(self.DATA_CLEAN_DIR + 'location')
            #create the participant folder follows by the date folder inside the location folder, if it doesn't exist
            if not os.path.exists(self.DATA_CLEAN_DIR + f'location/{participantID}/{date}'):
                os.makedirs(self.DATA_CLEAN_DIR + f'location/{participantID}/{date}')
            # save the motion_df as a csv file inside the location/participantID/date folder
            motion_df.to_csv(self.DATA_CLEAN_DIR + f'location/{participantID}/{date}/location_{date}.csv', index=False)
            # return the empty df
            return empty_df
        
        # turn the LOG_TIME column into a datetime object, removing the zone
        motion_df['LOG_TIME'] = pd.to_datetime(motion_df['LOG_TIME'])
        motion_df['LOG_TIME'] = motion_df['LOG_TIME'].dt.tz_localize(None)
        # reset the second and microsecond to 0
        motion_df['LOG_TIME'] = motion_df['LOG_TIME'].dt.floor('min')
        # delete the duplicate rows
        motion_df = motion_df.drop_duplicates(subset=['LOG_TIME'])
        # impute missing rows (interval of 1 minute)
        motion_df = self.impute_missing_rows(motion_df, date)
        # replace the -1 entry with 0
        motion_df = motion_df.replace(-1, 0)
        #divide all numbers by 100
        motion_df = motion_df.div(100)
        # replace NaN with -1
        motion_df = motion_df.fillna(-1)
        # create a folder inside the data/clean folder named motion
        if not os.path.exists(self.DATA_CLEAN_DIR + 'motion'):
            os.makedirs(self.DATA_CLEAN_DIR + 'motion')
        
        #create the participant folder follows by the date folder inside the motion folder, if it doesn't exist
        if not os.path.exists(self.DATA_CLEAN_DIR + f'motion/{participantID}/{date}'):
            os.makedirs(self.DATA_CLEAN_DIR + f'motion/{participantID}/{date}')
        
        # save the motion_df as a csv file inside the motion/participantID/date folder
        motion_df.to_csv(self.DATA_CLEAN_DIR + f'motion/{participantID}/{date}/motion_{date}.csv', index=False)
        return motion_df
        
    def impute_missing_rows(self, motion_df, date):
        # get the datetime object from date
        date = pd.to_datetime(date, format='%Y-%m-%d')
        # create a df with 1440 rows and 1 column named TIME, starting from 0:00 of the date and ending at 23:59 of the date
        time_df = pd.DataFrame(columns=['TIME'], index=range(1440))
        time_df['TIME'] = pd.date_range(start=date, end=date + pd.Timedelta('23:59:00'), freq='1min')
        #merge the time_df with the motion_df on the LOG_TIME and TIME columns
        motion_df = pd.merge(time_df, motion_df, how='left', left_on='TIME', right_on='LOG_TIME')
        # drop the TIME column
        motion_df = motion_df.drop(columns=['LOG_TIME'])
        print(len(motion_df))
        return motion_df

    def process_all_user(self, participantID):
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
                self.get_motion_at_date(participantID, date)

obj = Motion()
# print(
obj.process_all_user('afflictedrevenueepilepsy')
# )