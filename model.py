__author__ = 'eliashussen'

import numpy as np
import pandas as p
from sklearn import linear_model, svm, tree
import etl


def linear_reg(data):

    # data = etl.prepare_data_for_modeling()

    stats = {}

    m_data = normalize_matrix(data)

    lr = linear_model.LinearRegression()

    li = range(m_data.shape[1])
    li.remove(3)

    y = m_data[:-1, 3]
    x = m_data[:-1:, li]

    xtest = m_data[-1, li]
    ytest = np.array(m_data[-1, 3]).reshape(1,)

    lr.fit(x, y)

    print('Coefficients: \n', lr.coef_)
    # The mean square error
    print("Residual sum of squares: %.2f"
          % np.sqrt((lr.predict(xtest) - ytest) ** 2))
    # Explained variance score: 1 is perfect prediction
    print('Variance score: %.2f' % lr.score(xtest, ytest))

    stats = {'coefs': np.round(lr.coef_, 4).tolist(),
             'rmse': np.round(np.sqrt((lr.predict(xtest) - ytest) ** 2)[0], 4),
             'variance score': lr.score(xtest, ytest),
             'Actual': np.round(ytest[0]),
             'Predicted': np.round(lr.predict(xtest)[0])
             }

    return stats


def normalize_matrix(data):

    data_m = data.values

    li = range(data_m.shape[1])
    li.remove(3)

    for c in li:

        col = (data_m[:, c] - np.min(data_m[:, c])) / (np.max(data_m[:, c]) - np.min(data_m[:, c]))

        data_m[:, c] = col

    return data_m

