import os, sys, traceback
import json
import shutil
from datetime import datetime
import pyzipper

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/../..'
DATA_INTER_DIR = ROOT_DIR + '/data/raw/intermediate_file/'
STUDY_DIR = ROOT_DIR + '/data/clean/study/'

def process_location(participantID):
    '''
    remove the date from the intermediate file
    '''
    # get the json object from the study_dates.json inside the study folder
    with open(STUDY_DIR + 'study_dates.json') as f:
        study_dates = json.load(f)
        # get the list inside the participantID key
        date_list = study_dates[participantID]
        # get the start_date and end_date
        start_date = date_list[0]
        end_date = date_list[1]
    
    #convert the start_date and end_date to datetime object
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # get the full participantID
    participantID_fule = participantID + "@timestudy_com"
    # get the list of folder inside the intermediate_file folder
    folder_list = os.listdir(DATA_INTER_DIR + participantID_fule)
    # check if the folder date is within the start_date and end_date,
    # if not, remove the folder
    for folder in folder_list:
        if (folder == '.DS_Store'):
            continue
        #convert the folder name to datetime object
        folder_date = datetime.strptime(folder, '%Y-%m-%d')
        if folder_date < start_date or folder_date > end_date:
            # remove recursively
            shutil.rmtree(DATA_INTER_DIR + participantID_fule + '/' + folder)
            continue
        # remove the non-GPS file
        try:
            unzip_GPS_file(DATA_INTER_DIR + participantID_fule + '/' + folder)
        except:
            continue

def unzip_GPS_file(folder_path):
    # get the list of files inside the folder
    file_list = os.listdir(folder_path)
    #remove any folder that is not zip file
    for file in file_list:
        if not "GPS" in file:
            os.remove(folder_path + '/' + file)
    file_list = os.listdir(folder_path)
    # get the path to the zip file
    zip_file_path = folder_path + '/' + file_list[0]
    # unzip the file
    unzip_file(zip_file_path)

def unzip_file(path):
    # unzip the file using the password "TIMEisthenewMICROTStudy-NUUSC" 
    with pyzipper.AESZipFile(path, 'r',
                                compression=pyzipper.ZIP_DEFLATED,
                                encryption=pyzipper.WZ_AES) as zip_ref:
            try:
                #chdir to the folder
                os.chdir(os.path.dirname(path))
                # set password
                zip_ref.setpassword(str.encode("TIMEisthenewMICROTStudy-NUUSC"))
                # extract the file
                zip_ref.extractall()
                # move back to the root directory
                os.chdir(ROOT_DIR)
            except:
                print(path)
                return
            
# process_location('afflictedrevenueepilepsy')
# unzip_file()