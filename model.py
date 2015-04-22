__author__ = 'eliashussen'

import numpy as np
import pandas as p
from sklearn import linear_model, svm, tree

import etl

def manage():

    data = etl.prepare_data_for_modeling()

    m_data = normalize_matrix(data)



def normalize_matrix(data):

    data_m = data.values

    for c in range(data_m.shape[1]):

        col = (data_m[:, c] - np.min(data_m[:, c])) / (np.max(data_m[:, c]) - np.min(data_m[:, c]))

        data_m[:, c] = col

    return data_m

