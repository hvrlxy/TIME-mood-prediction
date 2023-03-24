import os
import traceback
import pandas as pd
import numpy as np
import warnings
from participant import Participant
import json

warnings.filterwarnings("ignore")

class Labels:
    def __init__(self):
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        self.DATA_RAW_DIR = self.ROOT_DIR + '/data/raw/'
        self.DATA_FILTER_DIR = self.ROOT_DIR + '/data/filtered/'
        self.DATA_CLEAN_DIR = self.ROOT_DIR + '/data/clean/'
        self.REPORTS_DIR = self.ROOT_DIR + '/reports/'
        self.participant = Participant()

    def get_survey_clean(self, participantID):
        # get the participant survey data inside the clean/EMA folder
        survey_df = pd.read_csv(self.DATA_CLEAN_DIR + f'EMA/{participantID}.csv')
        return survey_df
    
    def get_stress_labels(self, participantID):
        # get the participant survey data inside the clean/EMA folder
        survey_df = self.get_survey_clean(participantID)
        # get only the initial_prompt_date, x07_stressed and participantID columns
        stress_labels = survey_df[['participantID', 'initial_prompt_date', 'x07_stressed']]
        #remove all rows with -1 values in the x07_stressed column
        # stress_labels = stress_labels[stress_labels['x07_stressed'] != -1]
        # create a label folder inside the data/clean folder
        if not os.path.exists(self.DATA_CLEAN_DIR + 'labels'):
            os.makedirs(self.DATA_CLEAN_DIR + 'labels')

        # create a participant folder inside the label folder
        if not os.path.exists(self.DATA_CLEAN_DIR + f'labels/{participantID}'):
            os.makedirs(self.DATA_CLEAN_DIR + f'labels/{participantID}')

        # save the stress_labels as a csv file inside the label/participantID folder
        stress_labels.to_csv(self.DATA_CLEAN_DIR + f'labels/{participantID}/stress_labels.csv', index=False)
        # return the stress labels
        return stress_labels
    
    def get_procastinate_labels(self, participantID):
        # get the participant survey data inside the clean/EMA folder
        survey_df = self.get_survey_clean(participantID)
        # get only the initial_prompt_date, x07_stressed and participantID columns
        procastinate_labels = survey_df[['participantID', 'initial_prompt_date', 'x12_procrastinate']]
        # remove all rows with -1 values in the x12_procrastinate column
        # procastinate_labels = procastinate_labels[procastinate_labels['x12_procrastinate'] != -1]
        # create a label folder inside the data/clean folder
        if not os.path.exists(self.DATA_CLEAN_DIR + 'labels'):
            os.makedirs(self.DATA_CLEAN_DIR + 'labels')

        # create a participant folder inside the label folder
        if not os.path.exists(self.DATA_CLEAN_DIR + f'labels/{participantID}'):
            os.makedirs(self.DATA_CLEAN_DIR + f'labels/{participantID}')

        # save the stress_labels as a csv file inside the label/participantID folder
        procastinate_labels.to_csv(self.DATA_CLEAN_DIR + f'labels/{participantID}/procastinate_labels.csv', index=False)
        # return the stress labels
        return procastinate_labels

    def process_all_user(self):
        # get the study_dates.json file as a dict
        with open(self.DATA_CLEAN_DIR + f'study/study_dates.json') as json_file:
            # get the list of all participants as keys
            participants = json.load(json_file).keys()
            # iterate through each participant
            for participantID in participants:
                #get the stress labels for the participant
                self.get_stress_labels(participantID)
                #get the procastinate labels for the participant
                self.get_procastinate_labels(participantID)

obj = Labels()
obj.process_all_user()