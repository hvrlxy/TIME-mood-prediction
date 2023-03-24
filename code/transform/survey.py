import os
import traceback
import pandas as pd
import warnings
import json
import numpy as np
import collections
import warnings

#ignore warnings
warnings.filterwarnings('ignore')

class TransformSurvey:
    def __init__(self):
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        self.DATA_RAW_DIR = self.ROOT_DIR + '/data/raw/'
        self.DATA_FILTER_DIR = self.ROOT_DIR + '/data/filtered/'
        self.DATA_CLEAN_DIR = self.ROOT_DIR + '/data/clean/'
        self.DATA_TRAINED_DIR = self.ROOT_DIR + '/data/trained/'
        self.REPORTS_DIR = self.ROOT_DIR + '/reports/'
    
    def get_survey_df(self, participantID):
        # read the survey data from the clean/EMA/participant folder
        survey_df = pd.read_csv(self.DATA_CLEAN_DIR + f'EMA/{participantID}.csv')
        return survey_df
    
    def process_survey_data(self, participantID):
        #get the survey_df
        survey_df = self.get_survey_df(participantID)
        #turn the initial_prompt_date column into a datetime object
        survey_df['initial_prompt_date'] = pd.to_datetime(survey_df['initial_prompt_date'])
        #if there is any duplicate initial_prompt_date, only take the last one
        survey_df = survey_df.drop_duplicates(subset='initial_prompt_date', keep='last')
        # initialize the numpy array that stores the 3D survey data
        survey_data = []
        # get initial_prompt_date column as a list
        survey_dates = survey_df['initial_prompt_date'].tolist()
        #remove the first 7 lines
        survey_dates = survey_dates[7:]
        # get the stress column as a list
        stress = survey_df['x07_stressed'].tolist()
        #remove the first 7 lines
        stress = stress[7:]
        # plus 1 to the stress column
        stress = [x + 1 for x in stress]
        #save the numpy array to a npz file
        np.savez_compressed(self.DATA_TRAINED_DIR + f'{participantID}/stress.npz', stress)
        #for each row in the stress_df
        for date in survey_dates:
            # process the 7 day survey data
            survey_data.append(self.process_7_day_survey_data(date, survey_df))

        # return the survey data as a numpy 4D array
        survey_data = np.asarray(survey_data)
        #create a participant folder inside the trained folder
        if not os.path.exists(self.DATA_TRAINED_DIR + f'{participantID}'):
            os.makedirs(self.DATA_TRAINED_DIR + f'{participantID}')
        #save the survey data as a numpy compressed file inside the trained folder
        np.savez_compressed(self.DATA_TRAINED_DIR + f'{participantID}/survey_data.npz', survey_data)

        return survey_data
        
    def process_7_day_survey_data(self, date, survey_df):
        # initialize the numpy array that stores the 2D survey data
        survey_data = []
        participantID = survey_df['participantID'].iloc[0]
        # get the survey data from the last 7 days from the date
        for i in range(7, 0, -1):
            # get the date of the row
            idate = date - pd.Timedelta(days=i)
            # strip to string
            idate = idate.strftime('%Y-%m-%d')
            # get the row with initial_prompt_date as idate
            row = survey_df[survey_df['initial_prompt_date'] == idate]
            # only get entries with columns starts with x
            row = row.filter(regex='^x')
            #turn the row into a numpy array
            row = row.to_numpy()
            # append the row to the survey_data
            survey_data.append(row)

        # return the survey data as a numpy 3D array

        return np.array(survey_data).transpose(0, 1, 2)

    def process_all_user_survey_data(self):
        # get the study_dates.json file as a dict
        with open(self.DATA_CLEAN_DIR + f'study/study_dates.json') as json_file:
            # get the list of all participants as keys
            participants = json.load(json_file).keys()
            # create an empty numpy array to store all the survey data
            # all_survey_data = []
            # iterate through each participant
            for participantID in participants:
                #get the survey data of the participant
                print(f'Processing survey data for participant {participantID}')
                try:
                    survey_data = self.process_survey_data(participantID)
                    # extend the all_survey_data with the survey data of the participant
                    # all_survey_data.extend(survey_data)
                except Exception as e:
                    print(f'Error processing survey data for participant {participantID}')
                    continue
obj = TransformSurvey()

# print(survey_df.head())
# obj.process_survey_data('urchinvariablytrend')
obj.process_all_user_survey_data()