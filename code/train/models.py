import os
import tensorflow as tf
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import RepeatVector
from keras.utils import plot_model
from collections import Counter

from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import TimeDistributed
from keras.layers import Conv1D
from keras.layers import BatchNormalization
from keras.layers import MaxPooling1D, Reshape
from keras.layers import IntegerLookup
from keras.regularizers import l2, l1
from keras.optimizers import Adam
from keras import backend as K

out_loss = 'sparse_categorical_crossentropy'
out_activ = 'softmax'
mask_value = 0
class_weight = {0: 0.05,
                1: 0.5,
                2: 1,
                3: 1,
                4: 2,
                5: 2}

def masked_loss_function(y_true, y_pred):
    mask = K.cast(K.not_equal(y_true, mask_value), K.floatx())
    return K.categorical_crossentropy(y_true * mask, y_pred * mask)

def survey_model(x_shape,
             n_classes,
             n_hidden=128,
             learning_rate=0.01,
             n_steps=7,
             length=17,
             n_signals=1,
             regularization_rate=0.01,
             lstm_depth=1,
             metrics=['accuracy']):
    """ CNN1D_LSTM version 1: Divide 1 window into several smaller frames, then apply CNN to each frame
    - Input data format: [None, n_frames, n_timesteps, n_signals]"""

    _input_shape = x_shape[1:]
    m = Sequential()

    m.add(Reshape((n_steps, length, n_signals), input_shape=_input_shape))
    m.add(BatchNormalization())
    m.add(TimeDistributed(Conv1D(filters=32, kernel_size=5, activation='relu', padding='same')))
    m.add(TimeDistributed(MaxPooling1D(pool_size=2)))
    m.add(TimeDistributed(Dropout(0.5)))
    m.add(TimeDistributed(Conv1D(filters=32, kernel_size=3, activation='relu')))
    m.add(TimeDistributed(MaxPooling1D(pool_size=2)))
    m.add(TimeDistributed(Dropout(0.5)))
    m.add(TimeDistributed(Flatten()))
    for _ in range(lstm_depth-1):
        m.add(LSTM(n_hidden, return_sequences=True,
                   kernel_regularizer=l2(regularization_rate)))
    m.add(LSTM(n_hidden))
    m.add(Dropout(0.5))
    m.add(Dense(100, activation='relu',
                kernel_regularizer=l2(regularization_rate)))
    m.add(Dense(200, activation='relu',
                kernel_regularizer=l1(regularization_rate)))
    m.add(Dense(n_classes, activation=out_activ))

    m.compile(loss=out_loss,
              optimizer=Adam(learning_rate=learning_rate, amsgrad=True),
              metrics=metrics)
    # summarize model
    m.summary()
    plot_model(m, to_file='/survey_model.png', show_shapes=True)
    return m

def motion_model(x_shape,
             n_classes,
             n_hidden=128,
             learning_rate=0.01,
             n_steps=7,
             length=1440,
             n_signals=8,
             regularization_rate=0.01,
             cnn_depth=3,
             lstm_depth=1,
             metrics=['accuracy']):
    """ CNN1D_LSTM version 1: Divide 1 window into several smaller frames, then apply CNN to each frame
    - Input data format: [None, n_frames, n_timesteps, n_signals]"""

    _input_shape = x_shape[1:]
    m = Sequential()

    m.add(Reshape((n_steps, length, n_signals), input_shape=_input_shape))
    m.add(BatchNormalization())
    m.add(TimeDistributed(Conv1D(filters=32, kernel_size=3, activation='relu', padding='same')))
    m.add(TimeDistributed(MaxPooling1D(pool_size=2)))
    m.add(TimeDistributed(Dropout(0.5)))
    m.add(TimeDistributed(Conv1D(filters=64, kernel_size=3, activation='relu')))
    m.add(TimeDistributed(MaxPooling1D(pool_size=2)))
    m.add(TimeDistributed(Dropout(0.5)))
    m.add(TimeDistributed(Flatten()))
    m.add(LSTM(n_hidden))
    m.add(Dropout(0.5))
    m.add(Dense(100, activation='relu',
                kernel_regularizer=l2(regularization_rate)))
    m.add(Dense(200, activation='relu',
                kernel_regularizer=l1(regularization_rate)))
    m.add(Dense(n_classes, activation=out_activ))

    m.compile(loss=out_loss,
              optimizer=Adam(learning_rate=learning_rate, amsgrad=True),
              metrics=metrics)
    # summarize model
    # print(model.summary())
    plot_model(m, to_file='/motion_model.png', show_shapes=True)
    return m