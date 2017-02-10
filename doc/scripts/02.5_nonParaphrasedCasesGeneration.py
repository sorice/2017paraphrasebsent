#!/usr/bin/env pythonS3.5
# -*- coding: utf-8 -*-

"""Negative cases generation of paraphrased cases
Created on Wed Dec 01 2016
Modified by analysis on 
Finish on 
.. version: 0.1
.. release: 0.1-RC1 7/12/2016
.. author: Abel Meneses abad
"""

import pandas as pd
from pandas import DataFrame
from collections import defaultdict
import time
import sys
import os
from numpy import mean

"TODO: make test > python3 02.5_nonParaphrasedCasesGeneration.py test/Non-pairs.test test/True-corpus.test test/susp/ test/src/ test/out/"

class CorpusChange:
    def __init__(self, nonPairTextFile, TrueCasesCorpusFile, suspdir, srcdir, N):
        self.pairFile = nonPairTextFile         #list of text pairs path file 
        self.trueCase = TrueCasesCorpusFile     #positive cases path file
        self.suspdir = suspdir
        self.srcdir = srcdir                    
        self.path=['susp/','src/']
        self.CWM = DataFrame([])                #Common Word Matrix
        self.N = N
        self.M = 2
        self.bestNText = defaultdict(list)
        self.TrueCases = pd.read_csv(TrueCasesCorpusFile,names=['FragID','suspf','srcf','class'], delimiter='\t')
        self.TextPairs = pd.read_csv(self.pairFile,names=['susp','src'],delimiter=' ')
        self.suspf = ''
        self.srcf = ''
        self.newCases = {}                      #final result tuple (id,susp_frag,src_frag,class)
        self.bestEval = {}
        self.count = len(self.TrueCases)

    def loadCWMatrix(self,CWM):
        "Load the current Common Word Matrix"
        if len(CWM) == 0:
            self.CWM = matrixCommonWords(self.TextPairs,self.TrueCases)
            print('Matrix of Common Words generated.\n')
        else:
            self.CWM = CWM
            print('Matrix of Common Words loaded.\n')
        return 

    def bestNTextsPerTrueCase(self):
        """
        Get best N text pair per true case
        """
        
        for TrueCase in self.CWM.index:
            for x,(textPairCase,value) in enumerate(self.CWM.xs(TrueCase).sort_values(ascending=False).iteritems()):
                if x < self.N:
                    self.bestNText[TrueCase].append(int(textPairCase)) #textPairCase number is returned as str.

        #TODO: filtrar que cada par de textos se use solamente M veces

        print('Best N Text per True Case generated.\n')
        return self.bestNText

    def getFalseCases(self):
        #for every True case:
        for TRUECaseID in self.bestNText.keys():
            # for every doc in True case
            for DOC in self.bestNText[TRUECaseID]:
                #Init object getBestFrag

                ID,self.bestEval = self.bestFragPerTrueCase(DOC, TRUECaseID) #get best frag of a DOC per True Case
            
            #Append new False case to corpus
            appendCorpusCase(ID,self.bestEval)
            input()
        return

    def bestFragPerTrueCase(self, DOC, idTRUECase):
        """Return the best fragmet per textCase by TrueCase"""
        print('bestFragPerTrueCase')
        
        self.suspf = self.TrueCases.suspf[DOC]
        self.srcf = self.TrueCases.srcf[DOC]
        idx = int(idTRUECase)      
        susp = self.TextPairs.susp[idx]
        src = self.TextPairs.src[idx]
        
        #Susp
        self.fragMatrix = self.getFragFrom(0,susp,idx)
        self.featureFragMatrix = self.getFeatureVector(self.suspf)
        x,y = self.bestValue()
        self.bestEval['susp'] = self.fragMatrix[y][x]

        #Src
        self.fragMatrix = self.getFragFrom(1,src,idx)
        self.featureFragMatrix = self.getFeatureVector(self.srcf)
        x,y = self.bestValue()
        self.bestEval['src'] = self.fragMatrix[y][x]

        self.count+=1
        #Create pair fragment case id
        newCaseID = str(self.count)+self.TextPairs.susp[idx][-9:-4]+self.TextPairs.src[idx][-9:-4]
        print('*******************************************\n',self.suspf)
        print('*******************************************\n',self.srcf,'******************************\n')
        print('*******************************************\n',self.bestEval['susp'])
        print('*******************************************\n',self.bestEval['src'],'******************************\n')
        input()
        return newCaseID

    def getFragFrom(self, file_type, text,idx):
        "Construct & return a matrix compose by every possible fragment made by aligned sentences"
        print('getFragFrom')

        self.fragMatrix = DataFrame([])
        
        if file_type == 0:
            textpath = self.suspdir; column = 'susp'
        else: textpath = self.srcdir; column = 'src'
        
        #Load aligned text structure corresponding to doc = idTrueCase
        text = pd.read_csv(os.path.join('../align',column,self.TextPairs[column][idx]),
                         names=['id','sent','offset','length'], 
                         sep='\t')

        #Generate de fragment matrix
        for idy in text.index: #for every sentence

            fragVector = []
            fragment = ''
            for x in range(len(text)):
                if x >= idy:
                    fragment += str(text['sent'][x]) + ' '
                    fragVector.append(fragment)
                else: fragVector.append('NaN')
                #print('idy:',idy, ',x:',x,',frag:',text['sent'][x])
            self.fragMatrix[idy]=fragVector
        
        return self.fragMatrix

    def getFeatureVector(self, frag):
        print('getFeatureVector')
        self.featureFragMatrix = DataFrame([])
        print('FRAGMENTO',frag)
        F1f = len(frag)
        F2f = frag.count(' ')
        F3f = frag.count('.')
        #Ff = mean([F1f,F2f,F3f])
        #F1f = F1f/Ff;F2f = F2f/Ff;F3f = F3f/Ff
        print('self.fragMatrix.index',len(self.fragMatrix.index))
        for x in self.fragMatrix.index:
            FValue_Vector = []
            for y in self.fragMatrix.xs(x).index:
                F1 = len(self.fragMatrix[y][x])
                F2 = self.fragMatrix[y][x].count(' ')
                F3 = self.fragMatrix[y][x].count('.')
                F = mean([F1,F2,F3])
                #F1 = F1/F;F2 = F2/F;F3 = F3/F
                FValue = (pow(F1/F1f* F2/F2f * F3/F3f, 1/3)*3)/sum([F1/(F1f) , F2/(F2f) , F3/F3f])
                #print('FV',FValue)
                print(x,y,':',F1,F2,F3,'|', F1f,F2f,F3f,'|', F1/F1f, F2/F2f, F3/F3f,'|', FValue)
                FValue_Vector.append(FValue)
            self.featureFragMatrix[x] = FValue_Vector
        return self.featureFragMatrix

    def bestValue(self):
        maxv = 0
        #print('++++++++++',len(self.featureFragMatrix.columns))
        for idx in self.featureFragMatrix.columns:
            for idy in self.featureFragMatrix[idx].keys():
                #print('----',self.featureFragMatrix[idx][idy])
                if self.featureFragMatrix[idx][idy] > maxv:
                    maxv = self.featureFragMatrix[idx][idy]
                    xmax = idx;ymax = idy
                    print('maxs:', xmax,ymax)
        return xmax,ymax

def appendCorpusCase(newCaseID, bestEval):
    """Write the positive cases corpus
    """
    #TODO: send CorpusName as a parameter
    
    paraphCorpus = open(outdir+'/PAN-None-Paraphrase-Corpus','a')
    newCase = newCaseID+'\t'+bestEval['susp']+'\t'+bestEval['src']+'\t'+str(0)+'\n'
    paraphCorpus.write(newCase)
    paraphCorpus.close()

#Utils
def matrixCommonWords(TextPairs, TrueCases):
    """ Get the common Word Matrix columns = TrueCases, index = textCase.
    """
    
    for idy in self.TextPairs.index:
        susp = os.path.join(suspdir, self.TextPairs.susp[idy])
        src = os.path.join(srcdir, self.TextPairs.src[idy])

        wordSusp = set(open(susp).read().split())
        wordSrc = set(open(src).read().split())

        CW_Vector = []
        
        for idx in self.TrueCases.index:
            CW_Vector.append(self.calcCommonWords(TrueCases.xs(idx),wordSusp,wordSrc))
        
        CWM[idy] = CW_Vector
        #print('column',idy,'=',self.CWM[idy])

    #save CWM into a file for future uses
    col = [x for x in range(0,len(self.TextPairs))]
    CWM.to_csv(path_or_buf='CWM.csv',cols=col)

    return CMW

def calcCommonWords(trueCase, wordSusp, wordSrc):
    "Get similarity between vocabularies."
    U = set(trueCase['suspf'].split())
    T = set(trueCase['srcf'].split())
    Q = wordSusp
    R = wordSrc
    return len(Q.intersection(U))/float(len(U))+len(R.intersection(T))/float(len(T))




if __name__ == "__main__":
    """ Process the commandline arguments. We expect five arguments: 
    - The path pointing to the negative pairs file, 
    - The paths pointing to the positive cases corpus, obtained before this script.
    - the actual source and suspicious documents are located,
    - and the path pointing to output directory.

    $ python3 script.py nonPairTextFile positiveCorpusFile susp src outdir
    """
    initt = time.time()

    if len(sys.argv) == 6:
        nonPairTextFile = sys.argv[1]
        trueCasesCorpusFile = sys.argv[2]
        suspdir = sys.argv[3]
        srcdir = sys.argv[4]
        outdir = sys.argv[5]
        N = 2
        CWM = DataFrame([])
        
        if outdir[-1] != "/":
            outdir+="/"
        
        #Initializing a corpus transformation object
        pipeline = CorpusChange(nonPairTextFile,trueCasesCorpusFile, suspdir, srcdir, N)

        # Read Common Word Matrix if exists.
        try:
            CWM = pd.read_csv('CWM.csv',header=0,index_col=0)
            print(len(CWM))
            input()
        except:
            pass
        pipeline.loadCWMatrix(CWM)
        pipeline.bestNTextsPerTrueCase()
        pipeline.getFalseCases()

    else:
        print('\n'.join(["Unexpected number of commandline arguments.",
                         "Usage: ./02.3_alignNormalizedCaseList.py {Non-pairs} {True-pairs} {src-dir} {susp-dir} {out-dir}"]))
    timef = time.time() - initt
    print ('tiempo total: ',timef)
