'''
This script shows the CNN feature extraction model for the survey data.
'''
import os
import numpy as np
from collections import Counter

from models import *

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/../..'
DATA_RAW_DIR = ROOT_DIR + '/data/raw/'
DATA_FILTER_DIR = ROOT_DIR + '/data/trained/'

# open the input file and print out the shape
X = np.load("/survey_data.npz")['arr_0']
y = np.load("/stress.npz")['arr_0']
input_shape = X.shape

print(Counter(y))
# get the number of labels in y
n_labels = len(np.unique(y))

model = survey_model(input_shape, n_labels)
model.fit(X, y, epochs=150, verbose=1, class_weight=class_weight)
