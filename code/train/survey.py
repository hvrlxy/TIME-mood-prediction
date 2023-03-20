'''
This script shows the CNN feature extraction model for the survey data.
'''
import tensorflow as tf
from keras.models import Sequential
from keras.models import Model
from keras.layers import Dense
from keras.layers import RepeatVector
from keras.utils import plot_model

from keras.layers import Input

from keras.layers import Conv1D
from keras.layers import MaxPooling1D
from keras.layers import Flatten
from keras.layers import Dropout


