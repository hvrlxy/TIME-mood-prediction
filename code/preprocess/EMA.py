import os
import traceback
import pandas as pd
import warnings
from logger import Logger
from participant import Participant
from globals import *
import json

warnings.filterwarnings("ignore")

class EMA:
    def __init__(self):
        self.logger = Logger().getLog('EMA')
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        self.DATA_RAW_DIR = self.ROOT_DIR + '/data/raw/'
        self.DATA_FILTER_DIR = self.ROOT_DIR + '/data/filtered/'
        self.DATA_CLEAN_DIR = self.ROOT_DIR + '/data/clean/'
        self.REPORTS_DIR = self.ROOT_DIR + '/reports/'
        self.participant = Participant()

    def get_EMA_results(self, participantID):
        self.logger.info('get_EMA_results(): ' + participantID)
        # check if the participantID is in the list of completed participants
        if participantID not in self.participant.get_completed_participant_list():
            self.logger.error('get_EMA_results(): participantID is not in the list of completed participants')
            return None
        try:
            EMA_df = pd.read_csv(self.DATA_FILTER_DIR + f'EMA/{participantID}@timestudy_com_ema_daily.csv')
        except Exception as e:
            self.logger.error(traceback.format_exc())
            self.logger.error('get_EMA_results(): Cannot find EMA results for ' + participantID)
            return None
        # only get the initial_prompt_date, answer_status and all columns starting with x
        EMA_df = EMA_df[['initial_prompt_date', 'answer_status'] + [col for col in EMA_df.columns if col.startswith('x')]]
        return EMA_df
    
    def impute_missing_date(self, EMA_df):
        # turn the initial_prompt_date column into a datetime object
        EMA_df['initial_prompt_date'] = pd.to_datetime(EMA_df['initial_prompt_date'])
        # get the column as a list
        date_list = EMA_df['initial_prompt_date'].tolist()
        current_date = date_list[0]
        current_index = 1
        # loop through the date_list
        while (current_index < len(date_list)):
            # if the current date is more than 1 day away from the previous date, add the missing dates
            # to the EMA_df, with other columns filled with NaN
            if (date_list[current_index] - current_date).days > 1:
                for i in range(1, (date_list[current_index] - current_date).days):
                    EMA_df = EMA_df.append({'initial_prompt_date': current_date + pd.Timedelta(days=i), 'answer_status': 'NeverStarted'}, ignore_index=True)
            current_date = date_list[current_index]
            current_index += 1
        # sort the EMA_df by the initial_prompt_date
        EMA_df = EMA_df.sort_values(by=['initial_prompt_date'])
        #turn the initial_prompt_date column back into a string with format YYYY-MM-DD
        EMA_df['initial_prompt_date'] = EMA_df['initial_prompt_date'].dt.strftime('%Y-%m-%d')
        return EMA_df
    
    def remove_tail_rows(self, EMA_df):
        '''
        remove the rows at the end of the df with 
        answer_status = NeverStarted or PartiallyCompleted
        '''
        #check if the number of rows with answer_status = NeverStarted or PartiallyCompleted is 0
        if len(EMA_df[EMA_df['answer_status'].isin(['NeverStarted', 'PartiallyCompleted'])]) == 0:
            return EMA_df
        # get the index of the last row with answer_status = NeverStarted or PartiallyCompleted
        last_index = EMA_df[EMA_df['answer_status'].isin(['NeverStarted', 'PartiallyCompleted'])].index[-1]
        #get the last index of the EMA_df
        last_index_of_df = EMA_df.index[-1]
        #if the last_index is not the last index of the EMA_df, remove the rows after the last_index
        while last_index == last_index_of_df:
            EMA_df = EMA_df.drop(last_index_of_df)
            last_index_of_df = EMA_df.index[-1]
            last_index = EMA_df[EMA_df['answer_status'].isin(['NeverStarted', 'PartiallyCompleted'])].index[-1]
        return EMA_df
    
    def encode_EMA_results(self, participantID):
        #get EMA df
        EMA_df = self.get_EMA_results(participantID)
        if EMA_df is None:
            return None
        #only get the initial_prompt_date, answer_status and all columns inside question_map
        EMA_df = EMA_df[['initial_prompt_date', 'answer_status'] + [col for col in EMA_df.columns if col in question_map]]
        # for each column start with x
        for col in EMA_df.columns:
            if col in question_map:
                EMA_df[col] = EMA_df[col].map(question_map[col])

        #impute the missing date
        EMA_df = self.impute_missing_date(EMA_df)
        #remove the tail rows
        EMA_df = self.remove_tail_rows(EMA_df)
        #add an ID column to the front of the EMA_df
        EMA_df.insert(0, 'participantID', participantID)
        #impute NaN with -1 for all columns
        EMA_df = EMA_df.fillna(-1)
        #create an EMAs folder inside the clean folder
        if not os.path.exists(self.DATA_CLEAN_DIR + 'EMA/'):
            os.makedirs(self.DATA_CLEAN_DIR + 'EMA/')
        EMA_df.to_csv(self.DATA_CLEAN_DIR + f'EMA/{participantID}.csv', index=False)
        return EMA_df
    
    def summary_all_participants(self):
        # get the list of completed participants
        participant_list = self.participant.get_completed_participant_list()
            
        summary_df = pd.DataFrame(columns=['participantID', 'EMA_count', 'EMA_completed_count', 'EMA_partial_count', "EMA_completed_percent"])
        for participantID in participant_list:
            df = self.get_EMA_results(participantID)
            if df is None:
                summary_df = summary_df.append({'participantID': participantID, 'EMA_count': 0, 'EMA_completed_count': 0, "EMA_completed_percent": 0, 'EMA_partial_count': 0}, ignore_index=True)
                continue
            else:
                summary_df = summary_df.append({'participantID': participantID, 'EMA_count': len(df), 
                                                'EMA_completed_count': len(df[df['answer_status'] == 'Completed']), 
                                                'EMA_partial_count': len(df[df['answer_status'] == 'PartiallyCompleted']), 
                                                "EMA_completed_percent": len(df[df['answer_status'] == 'Completed'])/len(df) * 100}, 
                                                ignore_index=True)
        # sort the participants ID in alphabetical order
        summary_df = summary_df.sort_values(by=['participantID'])
        # create an EMA folder in the reports folder
        if not os.path.exists(self.REPORTS_DIR + 'EMA'):
            os.makedirs(self.REPORTS_DIR + 'EMA')
        # save the summary_df to a csv file and xlsx file
        summary_df.to_csv(self.REPORTS_DIR + 'EMA/summary_all_participants.csv', index=False)
        summary_df.to_excel(self.REPORTS_DIR + 'EMA/summary_all_participants.xlsx', index=False)

        return summary_df

    def process_all_participants_ema(self):
        # get the list of completed participants
        participant_list = self.participant.get_completed_participant_list()
        #create a df to store the EMA results
        df = pd.DataFrame()
        #create a json object with participantID as key and a list of start_date and end_date as value
        participant_dict = {}
        #loop through all the participants
        for participantID in participant_list:
            # process the EMA results
            try:
                subject_df = self.encode_EMA_results(participantID)
                # get the first entry of the initial_prompt_date column
                start_date = subject_df['initial_prompt_date'].iloc[0]
                # get the last entry of the initial_prompt_date column
                end_date = subject_df['initial_prompt_date'].iloc[-1]
                # append the participantID, start_date, end_date to the participant_dict
                participant_dict[participantID] = [start_date, end_date]
            except FileNotFoundError:
                self.logger.error('process_all_participants_ema(): Cannot find EMA results for ' + participantID)
                continue
            except Exception as e:
                self.logger.error('process_all_participants_ema(): ' + str(e))
                continue
            # append the subject_df to the df
            df = df.append(subject_df)
        #save the df to a csv file called all.csv
        if not os.path.exists(self.DATA_CLEAN_DIR + 'EMA/'):
            os.makedirs(self.DATA_CLEAN_DIR + 'EMA/')
        df.to_csv(self.DATA_CLEAN_DIR + 'EMA/all.csv', index=False)

        # create a study folder in the clean folder
        if not os.path.exists(self.DATA_CLEAN_DIR + 'study/'):
            os.makedirs(self.DATA_CLEAN_DIR + 'study/')
        #save json object to a json file
        with open(self.DATA_CLEAN_DIR + 'study/study_dates.json', 'w') as fp:
            json.dump(participant_dict, fp)


obj = EMA()
obj.process_all_participants_ema()