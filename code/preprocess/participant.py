import os
import traceback
import pandas as pd
import numpy as np
import warnings
from logger import Logger

warnings.filterwarnings("ignore")

class Participant:
    def __init__(self):
        self.logger = Logger().getLog('participant')
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        self.DATA_RAW_DIR = self.ROOT_DIR + '/data/raw/'
        self.DATA_FILTER_DIR = self.ROOT_DIR + '/data/filtered/'
        
    def get_participant_df(self, filename = 'TIMEMAIN-ParticipantTracking_DATA_LABELS_2022-final.csv'):
        self.logger.info('get_participant_list(): ' + filename)
        try:
            participant_df = pd.read_csv(self.DATA_RAW_DIR + filename)
        except Exception as e:
            self.logger.error(traceback.format_exc())
            return None
        return participant_df
    
    def get_completed_participant_list(self):
        # get the processed participant_df
        participant_df = self.process_completed_participants()
        if participant_df is None:
            self.logger.error('get_completed_participant_list(): participant_df is None')
            return []
        return participant_df['Visualizer ID'].tolist()
    
    def process_completed_participants(self):
        self.logger.info('process_completed_participants()')
        participant_df = self.get_participant_df()
        if participant_df is None:
            self.logger.error('process_completed_participants(): participant_df is None')
            return None
        
        # only get the columns = 'Visualizer ID', 'Participant Status '
        participant_df = participant_df[['Visualizer ID', 'Participant Status ']]
        # only get the one with Completed status
        participant_df = participant_df[participant_df['Participant Status '] == 'Completed']
        
        # create a folder called participantID in data/filter
        if not os.path.exists(self.DATA_FILTER_DIR + 'participantID'):
            os.makedirs(self.DATA_FILTER_DIR + 'participantID')
        
        #save the participant_df to data/filter/participantID
        participant_df.to_csv(self.DATA_FILTER_DIR + 'participantID/participantID.csv', index = False)
        self.logger.info('process_completed_participants(): Save the participant_df to ' + self.DATA_FILTER_DIR + 'participantID/participantID.csv')
        return participant_df
    
    def filtered_EMA_raw(self):
        # get the list of completed participants
        participant_df = self.process_completed_participants()

        # get all csv file in the raw/EMA folder
        EMA_list = os.listdir(self.DATA_RAW_DIR + 'EMA')
        EMA_list = [x for x in EMA_list if x.endswith('.csv')]

        # only get the EMA files with names starting with the participantID in the participant_df's Visualizer ID column
        EMA_list = [x for x in EMA_list if x.split('@')[0] in participant_df['Visualizer ID'].tolist()]

        #create a folder called EMA in data/filter
        if not os.path.exists(self.DATA_FILTER_DIR + 'EMA'):
            os.makedirs(self.DATA_FILTER_DIR + 'EMA')
        
        # copy the EMA files to data/filter/EMA
        for EMA in EMA_list:
            try:
                os.system('cp ' + self.DATA_RAW_DIR + 'EMA/' + EMA + ' ' + self.DATA_FILTER_DIR + 'EMA/' + EMA)
                self.logger.info('filtered_EMA_raw(): Save the EMA files to ' + self.DATA_FILTER_DIR + 'EMA/')
            except Exception as e:
                self.logger.error(traceback.format_exc())
                continue
        return EMA_list
    
# TODO: uncomment this to filtered out all the EMA results for the completed participants
# obj = Participant()
# print(
# obj.filtered_EMA_raw()
# )