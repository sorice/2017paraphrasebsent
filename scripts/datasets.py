#!/usr/bin/env python 3.5

import csv
import numpy as np
from sklearn.datasets.base import Bunch

def load_msrpc(file_path='data/MSRPC-2004/msrpc_test_textsim-42f.csv'):
    """Load the Microsoft Research Paraphrase Corpus"""

    with open(file_path) as csv_file:
        data_file = csv.reader(csv_file)
        temp = next(data_file)
        n_samples = int(temp[0])
        n_features = int(temp[1])
        target_names = np.array(temp[2:4])
        feature_names = np.array(temp[4:-1])
        data = np.empty((n_samples, n_features))
        target = np.empty((n_samples,), dtype=np.int)

        for i, ir in enumerate(data_file):
            data[i] = np.asarray(ir[:-1], dtype=np.float)
            target[i] = np.asarray(ir[-1], dtype=np.int)

        fdescr = ''

    return Bunch(data=data, target=target,
                target_names=target_names,
                DESCR=fdescr,
                feature_names=feature_names)
