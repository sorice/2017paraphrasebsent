#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

"""Script function to preprocess a text-reuse collection texts given pare the data.
If the user enter a path to preprocess a list of document, or a doc the module will no fail.
Created on Fry Sept 02 2016
Modified by analysis on 
Finish on 
.. version: 0.1
.. release: 0.1-RC1
.. author: Abel Meneses abad
"""

import sys
sys.path.append('/home/abelm')
import re
import time
import os
from preprocess.example import preProcessFlow as textNormalizationProcess

class Process:
    def __init__(self, susp, src, outdir, normalizedDocList):
        self.susp = susp
        self.src = src
        self.susp_file = os.path.split(susp)[1]
        self.src_file = os.path.split(src)[1]
        self.outdir=outdir
        self.validText = True
        self.validProcess = []
        self.normalizedDocList = normalizedDocList
        self.filepath = ['susp/','src/']

    def process(self):

        validProcess = []
        for i,fileName in enumerate([self.susp, self.src]):
        	#Normalize if you didn't before
            if fileName not in self.normalizedDocList.keys():
                validProcess = self.preprocess(fileName,i)
            #Don't normalize again, take the value obtained before
            else:
                validProcess = self.normalizedDocList[fileName]

            self.validProcess.append(validProcess)

        return self.validProcess

    def preprocess(self, fileName, i):
        """ Text normalization pipeline. """

        with open(fileName) as _file:
            text = _file.read()
        
        #Normalizing Text
        textNorm = textNormalizationProcess(text)
        
        # Add fileName to preprocessed doc list
        self.normalizedDocList[fileName] = True

        #write the preprocessed text result in a new path with the same name
        doc = open(self.outdir+self.filepath[i]+os.path.split(fileName)[1],'w') 
        doc.write(textNorm)
        doc.close()

        return True

if __name__ == "__main__":
    """ Process the commandline arguments. We expect four arguments: The path
    pointing to the pairs file, the paths pointing to the directories where
    the actual source and suspicious documents are located and the path
    pointing to output directory.
    """
    initt = time.time()
    positive = 0

    if len(sys.argv) == 5:
        srcdir = sys.argv[2]
        suspdir = sys.argv[3]
        outdir = sys.argv[4]
        if outdir[-1] != "/":
            outdir+="/"
        lines = open(sys.argv[1], 'r').readlines()
        cases = len(lines)
        normalizedDocList = {}
        validCases = []

        txt = open(outdir+'normalizedDocList')
        doc = txt.read()
        for line in doc.split('\n'):
            if line[line.find(' ')+1:] == 'True':
                normalizedDocList[line[:line.find(' ')]] = True
            else:
            	if len(line) > 1:
                	normalizedDocList[line[:line.find(' ')]] = False
        txt.close()

        for i,line in enumerate(lines):
            try:
                susp, src = line.split()

                flow = Process(os.path.join(suspdir, susp),
                                    os.path.join(srcdir, src), outdir,
                                    normalizedDocList)
                validProcess = flow.process()
                result = validProcess[0]&validProcess[1]

                #if result is good then the text pairs contain in line is valid
                #then write a valid case
                if result:
                    positive+=1
                    validCases.append(line[:-1])              
                
                #Update normalizedDocList. Cases can share some of its texts.
                #The next two lines optimize normalization process if texts repeats.
                normalizedDocList[os.path.join(suspdir, susp)] = validProcess[0]
                normalizedDocList[os.path.join(srcdir, src)] = validProcess[1]
                
                #The next two lines are to print on the notebook    
                if i*10%cases <= 10 or i == len(lines)-1:
                    print(i+1,'/',cases,'TRUE:', positive)
           
            except: #blank lines for example
                pass

        #write valid cases in a text
        pairValidDoc = open(outdir+'norm_pairs','w')
        for case in validCases:
            pairValidDoc.write(case+'\n')
        pairValidDoc.close()

        #write pre processed doc list in a text to avoid future re-preprocessing
        doc = open(outdir+'normalizedDocList','w')
        for key,value in sorted(normalizedDocList.items()):
            doc.write(key+' '+str(value)+'\n')
        doc.close()

    else:
        print('\n'.join(["Unexpected number of commandline arguments.",
                         "Usage: ./02.1_preprocessCaseList.py {pairs} {src-dir} {susp-dir} {out-dir}"]))
    timef = time.time() - initt
    print ('tiempo total: ',timef)
