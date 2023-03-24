import os
import traceback
import pandas as pd
import warnings
import json
import numpy as np

class TransformMotion:
    def __init__(self):
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        self.DATA_RAW_DIR = self.ROOT_DIR + '/data/raw/'
        self.DATA_FILTER_DIR = self.ROOT_DIR + '/data/filtered/'
        self.DATA_CLEAN_DIR = self.ROOT_DIR + '/data/clean/'
        self.DATA_TRAINED_DIR = self.ROOT_DIR + '/data/trained/'
        self.REPORTS_DIR = self.ROOT_DIR + '/reports/'
    
    def get_stressed_labels(self, participantID):
        # get the stress labels from the clean/labels/participant folder
        stress_labels = pd.read_csv(self.DATA_CLEAN_DIR + f'labels/{participantID}/stress_labels.csv')
        # remove the first 7 lines
        stress_labels = stress_labels.iloc[7:]
        # reset the index
        stress_labels = stress_labels.reset_index(drop=True)

        return stress_labels
    
    def process_motion_data(self, participantID):
        # get the stress_df
        stress_df = self.get_stressed_labels(participantID)

        # turn the initial_prompt_date column into a datetime object
        stress_df['initial_prompt_date'] = pd.to_datetime(stress_df['initial_prompt_date'])
        # initialize the numpy array that stores the 3D motion data
        motion_data = []
        #for each row in the stress_df
        for index, row in stress_df.iterrows():
            # get the date of the row
            date = row['initial_prompt_date']
            # process the 7 day motion data
            motion_data.append(self.process_7_day_motion_data(date, participantID))

        # return the motion data as a numpy 4D array
        motion_data = np.asarray(motion_data)

        #create a participant folder inside the trained folder
        if not os.path.exists(self.DATA_TRAINED_DIR + f'{participantID}'):
            os.makedirs(self.DATA_TRAINED_DIR + f'{participantID}')
        #save the motion data as a numpy compressed file inside the trained folder
        np.savez_compressed(self.DATA_TRAINED_DIR + f'{participantID}/motion_data.npz', motion_data)
        
    def process_7_day_motion_data(self, date, participantID):
        # initialize the path to clean motion data of the participant
        path = self.DATA_CLEAN_DIR + f'motion/{participantID}/'

        # initialize the numpy array that stores the 2D motion data
        motion_data = []

        # get the motion data from the last 7 days from the date
        for i in range(7, 0, -1):
            # get the date of the row
            idate = date - pd.Timedelta(days=i)
            # get the date string
            date_str = idate.strftime('%Y-%m-%d')
            # get the motion data of the date (csv file)
            motion_df = pd.read_csv(path + f'{date_str}/motion_{date_str}.csv')
            # remove the TIME column
            motion_df = motion_df.drop(columns=['TIME'])
            # turn the other columns into numpy 2D array
            motion_data.append(motion_df.to_numpy())

        # return the motion data as a numpy 3D array
        # print(np.array(motion_data).transpose(0, 1, 2).shape)
        return np.array(motion_data).transpose(0, 1, 2)

    def process_all_user_motion_data(self):
        # get the study_dates.json file as a dict
        with open(self.DATA_CLEAN_DIR + f'study/study_dates.json') as json_file:
            # get the list of all participants as keys
            participants = json.load(json_file).keys()
            # iterate through each participant
            for participantID in participants:
                #get the motion data of the participant
                try:
                    self.process_motion_data(participantID)
                except Exception as e:
                    print(f'Error processing motion data for participant {participantID}')
                    print(e)
                    continue
        
obj = TransformMotion()
obj.process_all_user_motion_data()