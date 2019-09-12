#!/usr/bin/env pythonS3.6
# -*- coding: utf-8 -*-

"""Utilitie functions to standarize the IN-object to the preprocessing method.
If the user enter a path to preprocess a list of document, or a doc the module will no fail.

You must create susp and src folders inside aligned folder before start.

Created on Wed Nov 09 2016
.. author: Abel Meneses abad
"""

import sys
import time
import os
from align import sentenceAligner
from pipeline import Process

if __name__ == "__main__":
    """ Process the commandline arguments. We expect four arguments: The path
    pointing to the pairs file, the paths pointing to the directories where
    the actual source and suspicious documents are located and the path
    pointing to output directory.
    """
    initt = time.time()
    positive = 0
    print('The script will use as default the data folder as working directory')
    datadir = os.path.abspath(os.getcwd()+'/data/')

    if len(sys.argv) == 5:
        srcdir = os.path.join(datadir,sys.argv[2])
        suspdir = os.path.join(datadir,sys.argv[3])
        outdir = os.path.join(datadir,sys.argv[4])
        
        alignedDocDict = {}
        validCases = []

        txt = open(outdir+'alignedDocDict','a')
        txt.close()

        for line in open(outdir+'alignedDocDict'):
            if line.split()[1]=='True':
                alignedDocDict[line.split()[0]] = True
            else:
                alignedDocDict[line.split()[0]] = False

        count = 0
        for line in open(os.path.join(datadir,sys.argv[1])):
            susp, src = line.split()
            print('++++++++++++++',susp,src)

            flow = Process(os.path.join(suspdir, susp),
                                os.path.join(srcdir, src), outdir,
                                alignedDocDict,sentenceAligner)

            validProcess = flow.process()
            result = validProcess[0]&validProcess[1]

            #if result is true then pair case is valid
            if result: 
                positive+=1
                validCases.append(line[:-1])
                
            #update alignedDocDict
            alignedDocDict[os.path.join(suspdir, susp)] = validProcess[0]
            alignedDocDict[os.path.join(srcdir, src)] = validProcess[1]
            count += 1
            
            #Auxiliar code to follow process on terminal output
            #Useful when the number of pair cases are big
            if count%1000 == 0:
                print('Preprocessed cases: ',count,'Valid cases: ', positive)

        #write valid cases in a text
        pairValidDoc = open(outdir+'aligned_pairs','w')
        for case in validCases:
            pairValidDoc.write(case+'\n')
        pairValidDoc.close()

        #write pre processed doc list in a text to avoid future re-preprocessing
        doc = open(outdir+'alignedDocDict','w')
        for key,value in alignedDocDict.items():
            doc.write(key+' '+str(value)+'\n')
        doc.close()

    else:
        print('\n'.join(["Unexpected number of commandline arguments.",
                         "Usage: ./02.2_alignNormalizedCaseList.py {pairs} {src-dir} {susp-dir} {out-dir}"]))
    timef = time.time() - initt
    print ('tiempo total: ',timef)