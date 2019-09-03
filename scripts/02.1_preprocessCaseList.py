#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

"""Preprocess script for text-reuse collection texts given in pairs.

Based on first experiences this script check both texts part of a pair
case, and normalize it only if these has been processed before.
The memory of the script is the normalizedDocDict document.
(normalizedDocDict text will be saved after every use on "norm" folder)

You must create susp and src folders inside norm folder before start.

Created on Sept 2016
.. author: Abel Meneses abad
"""

import sys
import re
import time
import os
from preprocess.demo import preProcessFlow as textNormalizationProcess
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
    print(datadir)

    if len(sys.argv) == 5:
        srcdir = os.path.join(datadir,sys.argv[2])    #src dir
        suspdir = os.path.join(datadir,sys.argv[3])   #susp dir
        outdir = os.path.join(datadir,sys.argv[4])    #result dir
        
        normalizedDocDict = {}
        validCases = []

        #If not exist, create normalizedDocDict txt at first running
        #Else let the data intact
        txt = open(outdir+'normalizedDocDict','a')
        txt.close()

        #Doing a normalized Document Dict to control wich of repeated
        #text has been preprocessed
        #Useful the second time or 
        for line in open(outdir+'normalizedDocDict'):
            if line.split()[1]=='True':
                normalizedDocDict[line.split()[0]] = True
            else:
                normalizedDocDict[line.split()[0]] = False

        count = 0
        for line in open(os.path.join(datadir,sys.argv[1])): #open pairs

            susp, src = line.split()

            flow = Process(os.path.join(suspdir, susp),
                                os.path.join(srcdir, src), outdir,
                                normalizedDocDict,textNormalizationProcess)

            validProcess = flow.process()
            result = validProcess[0]&validProcess[1]

            #if result is good then the text pairs contain in line is valid
            #then write a valid case
            if result:
                positive+=1
                validCases.append(line[:-1])              
            
            # Update normalizedDocDict. 
            # Different cases can share a text member with other case.
            # Optimization for norm process if a text is repeated.
            normalizedDocDict[os.path.join(suspdir, susp)] = validProcess[0]
            normalizedDocDict[os.path.join(srcdir, src)] = validProcess[1]
            count += 1

            #Auxiliar code to follow process on terminal output
            #Useful when the number of pair cases are big
            if count%1000 == 0:
                print('Preprocessed cases: ',count,'Valid cases: ', positive)

        #Writing normalized pare cases in a text for future flows
        pairValidDoc = open(outdir+'norm_pairs','w')
        for case in validCases:
            pairValidDoc.write(case+'\n')
        pairValidDoc.close()

        #write pre processed doc list in a text to avoid future re-preprocessing
        doc = open(outdir+'normalizedDocDict','w')
        for key,value in sorted(normalizedDocDict.items()):
            doc.write(key+' '+str(value)+'\n')
        doc.close()

    else:
        print('\n'.join(["Unexpected number of commandline arguments.",
                         "Usage: ./02.1_preprocessCaseList.py {pairs} {src-dir} {susp-dir} {out-dir}"]))
    timef = time.time() - initt
    print ('tiempo total: ',timef)
