'''
Response options for 5 points scales
1 = Not at all
2 = A little
3 = Moderately 
4 = Quite a bit 
5 = Extremely
'''
five_point_Likert = {
    "Not at all": 1,
    "A little": 2,
    "Moderately": 3,
    "Quite a bit": 4,
    "Extremely": 5
}


'''
Response options for yes/no scales
1= Yes
2= No
'''
yes_no_Likert = {
    0: 0,
    1: 1
}

'''
Response options for illness scales
1= Yes
2= No
3= Not sure
'''
illness_Likert = {
    "Yes": 1,
    "No": 2,
    "Not sure": 3
}

'''
Response options for missed work
1= Yes
2= No
3= I didn’t have to go to work or school today
'''
missed_work_Likert = {
    "Yes": 1,
    "No": 2,
    "I didn’t have to go to work or school today": 3
}

'''
Map question ID to question likert
    five_point = 'x01_sad', 'x02_happy', 'x03_fatigued', 
                'x04_energetic', 'x05_relaxed', 'x06_tense'
                'x07_stressed', 'x08_frustrated', 'x09_nervous', 
                'x10_focused', 'x11_resist', 'x12_procrastinate', 
                'x13_done', 'x14_routine'
    yes_no = 'x17_traveled' 
    missed_work = 'x16_missed'
    illness = 'x15_sick'
'''
question_map = {
    'x01_sad': five_point_Likert,
    'x02_happy': five_point_Likert,
    'x03_fatigued': five_point_Likert,
    'x04_energetic': five_point_Likert,
    'x05_relaxed': five_point_Likert,
    'x06_tense': five_point_Likert,
    'x07_stressed': five_point_Likert,
    'x08_frustrated': five_point_Likert,
    'x09_nervous': five_point_Likert,
    'x10_focused': five_point_Likert,
    'x11_resist': five_point_Likert,
    'x12_procrastinate': five_point_Likert,
    'x13_done': five_point_Likert,
    'x14_routine': five_point_Likert,
    'x17_traveled': yes_no_Likert,
    'x16_missed': missed_work_Likert,
    'x15_sick': illness_Likert
}
