#!/usr/bin/env python 3.5

import csv
import numpy as np
from sklearn.datasets.base import Bunch

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

        fdescr = ''

    return Bunch(data=data, target=target,
                target_names=target_names,
                DESCR=fdescr,
                feature_names=feature_names)

import sys
sys.path.append('/home/abelm')
import pandas as pd
from pandas import DataFrame, Series, read_table
import textsim
from textsim.utils import calc_all
import arff
import os

def msrpc_to_csv(file_path='data/MSRPC-2004/msrpc_textsim.txt',out_path=''):
    """Convert corpus MSRP from TXT format to CSV format in sklearn Bunch
    structure.

    Example:
    >>> from scripts.datasets import msrpc_to_csv
    >>> msrpc_to_csv('../data/MSRPC-2004/msrpc_paraphrase.txt','../data/result2.csv')
    """

    #Read Paraphrase Corpus
    df = read_table(file_path,sep='\t')
    data = []
    distances = []
    exceptions = []

    for distance in sorted(textsim.__all_distances__.keys()):
        distances.append(distance)
    distances.append('id')
    distances.append('class')

    for row in range(len(df)):
        clase, ide1, ide2, sent1, sent2 = df.xs(row)
        try:
            obj = calc_all(sent1,sent2)[2:]
            obj.append(row)
            if clase:
                obj.append('yes')
            else:
                obj.append('no')
            data.append(obj)
        except:
            exceptions.append(row)

    if out_path == '':
        out_path = os.path.abspath(file_path)[:os.path.abspath(file_path).rfind('.')]+'.csv'

    with open(out_path,'w') as corpus: #Open vector similarity feature corpus
            corpus.write(str(len(data))+',')
            corpus.write(str(len(distances)-1)+',')
            corpus.write('Paraph,Non,')
            for distance in distances:
                corpus.write(distance+',')
            corpus.write('\n')
            for instance in data:
                corpus.write(str(instance)[1:-1]+'\n')

    return

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
