__author__ = 'eliashussen'

import numpy as np
import pandas as p
from sklearn import linear_model, svm, tree

import etl

def manage():

    data = etl.prepare_data_for_modeling()

    data = normalize(data)


def normalize(data):

    pass
