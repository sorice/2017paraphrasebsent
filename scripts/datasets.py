#!/usr/bin/env python 3.5
"""
The functions here are based on sklearn/datasets/_base.py
functions.
"""
import sklearn
import csv
import numpy as np
from sklearn.utils import Bunch
import sys
import pandas as pd
from pandas import DataFrame, Series, read_csv
import textsim
from textsim.utils import calc_all
import arff
import os


def load_msrpc(file_path='data/MSRPC-2004/msrpc_textsim.csv'):
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
            if 'yes' in ir[-1]:
                ir[-1] = 1
            elif 'no' in ir[-1]:
                ir[-1] = 0
            target[i] = np.asarray(ir[-1], dtype=np.int)

	#TODO: write the msrpc description file like iris.rst in ~/sklearn/datasets/descr
        fdescr = ''

    return Bunch(data=data, target=target,
                target_names=target_names,
                DESCR=fdescr,
                feature_names=feature_names)

def msrpc_to_csv(file_path ,out_path=''):
    """Convert corpus MSRP from TXT format to CSV format in sklearn Bunch
    structure.

    Example:
    >>> from scripts.datasets import msrpc_to_csv
    >>> msrpc_to_simvector('../data/MSRPC-2004/msrpc_paraphrase_test.txt','../data/MSRPC-2004/msrpc_paraphrase_test.csv')
    """

    if not file_path:
        print('Not msrpc corpus path provided.')
        return False

    try:
        df = read_csv(file_path,sep='\t')
    except:
        pass

    #Read Paraphrase Corpus
    distances = []
    exceptions = []

    distances.append('id')
    for distance in sorted(textsim.__all_distances__.keys()):
        distances.append(distance)
    distances.append('class')
    
    data = DataFrame(columns=distances)

    with open(file_path) as corp:
        for num,row in enumerate(corp):
            try:
                clase, ide1, ide2, sent1, sent2 = row.split('\t')
                if num == 0:
                    pass
                else:
                    obj = calc_all(sent1,sent2)[2:]
                    obj.append(num)
                    if clase:
                        obj.append(1)
                    else:
                        obj.append(0)
                    data = data.append(Series(obj, index=data.columns), ignore_index=True)
            except:
                exceptions.append(num)

    if not out_path:
        out_path = os.path.abspath(file_path)[:os.path.abspath(file_path).rfind('.')]+'.csv'

    data.to_csv(out_path)

    #TODO completar las dos primeras líneas para el estandar de sklearn

    return True

def msrpc_to_arff(file_path='data/MSRPC-2004/msrpc_textsim.txt',out_path=''):
    """Convert corpus MSRP from TXT format to ARFF Weka format."""

    #Read Paraphrase Corpus
    df = read_table(file_path,sep='\t')
    data = []
    distances = []
    exceptions = []

    if out_path == '':
        out_path = os.path.abspath(file_path)[:os.path.abspath(file_path).rfind('.')]+'.arff'

    with open(out_path,'w') as corpus: #Open vector similarity feature corpus
        corpus.write('@relation paraphrase\n\n')
        for distance in sorted(textsim.__all_distances__.keys()):
            corpus.write('@attribute '+distance+' numeric\n')
            distances.append(distance)
        corpus.write('@attribute '+'id'+' integer\n')
        distances.append('id')
        corpus.write('@attribute class {yes,no}\n\n')
        distances.append('class')
        corpus.write('@data\n')

        for row in range(len(df)):
            clase, ide1, ide2, sent1, sent2 = df.xs(row)
            try:
                obj = calc_all(sent1,sent2)[2:]
                sec = ''
                for item in obj:
                    if str(item) == 'nan':
                        sec += '?,'
                    else:
                        sec += str(item)+','
                sec += str(row) #append id for future analysis after classification
                obj.append(row)
                if clase:
                    corpus.write(sec+',yes\n')
                else:
                    corpus.write(sec+',no\n')
            except:
                pass

    return
