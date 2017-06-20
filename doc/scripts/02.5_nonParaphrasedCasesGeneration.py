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
    def __init__(self, nonParaphTextPairList, TrueCasesCorpusFile, suspdir, srcdir, N):
        self.pairFile = nonParaphTextPairList         #list of text pairs path file 
        self.trueCase = TrueCasesCorpusFile     #positive cases path file
        self.suspdir = suspdir
        self.srcdir = srcdir                    
        self.path=['susp/','src/']
        self.CWM = DataFrame([])                #Common Word Matrix
        self.N = N
        self.M = 2
        self.bestNNonParaphTextPairID = defaultdict(list)
        self.TrueCases = pd.read_csv(TrueCasesCorpusFile,names=['fragPairID','suspf','srcf','class'], delimiter='\t')
        self.TextPairs = pd.read_csv(self.pairFile,names=['susp','src'],delimiter=' ')
        self.suspf = ''
        self.srcf = ''
        self.newCases = {}                      #final result tuple (id,susp_frag,src_frag,class)
        self.bestEval = {}
        self.count = len(self.TrueCases)

    def loadCWMatrix(self,CWM):
        "Load the current Common Word Matrix"
        if len(CWM) == 0:
            print('Generating Matrix of Common Words.\n')
            self.CWM = matrixCommonWords(self.TextPairs,self.TrueCases)
            print('Matrix of Common Words generated.\n')
        else:
            self.CWM = CWM
            print('Matrix of Common Words loaded.\n')
        return 

    def bestNTextsPerTrueCase(self):
        """
        Get by True Case the best N IDs of non paraphrased text pair.
        """
        
        for trueCase in self.CWM.index:
            for x,(NonParaphTextPairID,value) in enumerate(self.CWM.xs(trueCase).sort_values(ascending=False).iteritems()):
                if x < self.N:
                    self.bestNNonParaphTextPairID[trueCase].append(int(NonParaphTextPairID)) #textPairCase id is returned as str.

        #TODO: filtrar que cada par de textos se use solamente M veces

        print('Best N Text per True Case generated.\n')
        return self.bestNNonParaphTextPairID

    def getFalseCases(self):
        """Get False cases or non paraphrased text pair cases"""
        print('Generating non paraphrased cases. This could take some hours depending on true cases amount')
        #for every True case:
        for TRUECaseID in self.bestNNonParaphTextPairID.keys():
            # for every doc in True case
            for NonParaphTextPairID in self.bestNNonParaphTextPairID[TRUECaseID]:
                #print('TRUECaseID',TRUECaseID,'NonParaphTextPairID',NonParaphTextPairID)
                #get best frag of a NonParaphTextPairID per True Case
                ID,self.FragmentTexts = self.bestFrag(TRUECaseID, NonParaphTextPairID)
                
                #Append new False case to corpus
                appendCorpusCase(ID,self.FragmentTexts)
        return

    def bestFrag(self, TRUECaseID, NonParaphTextPairID):
        """
        Based on a True Case ID calc its correspondent best chunks (src&susp) inside TextPair[ID].values file names.
        Return the ID for the new FalseCase based on susp & src names numbers (PAN-PC original file names IDs).
        """

        #Load true case susp & src text fragments
        self.suspf = self.TrueCases.suspf[TRUECaseID]
        self.srcf = self.TrueCases.srcf[TRUECaseID]
        #Load susp & src file names
        idx = int(NonParaphTextPairID)      
        susp = self.TextPairs.susp[idx]
        src = self.TextPairs.src[idx]

        #Susp
        self.fragMatrix = self.getFragFrom(susp,idx)
        self.featureFragMatrix = self.getFeatureVector(self.suspf)
        x,y = self.bestValue()
        self.bestEval['susp'] = self.fragMatrix[y][x]

        #Src
        self.fragMatrix = self.getFragFrom(src,idx)
        self.featureFragMatrix = self.getFeatureVector(self.srcf)
        x,y = self.bestValue()
        self.bestEval['src'] = self.fragMatrix[y][x]

        self.count+=1
        #Generate non paraphrased pair fragment case id
        newCaseID = str(self.count)+self.TextPairs.susp[idx][-9:-4]+self.TextPairs.src[idx][-9:-4]
        #~ print('**********************\n',susp,src,'\n',self.suspf)
        #~ print('**********************\n',self.srcf,'**********************\n')
        #~ print('**********************\n',self.bestEval['susp'])
        #~ print('**********************\n',self.bestEval['src'],'**********************\n')
        return newCaseID, self.bestEval

    def getFragFrom(self, textName,idx):
        """
        Construct & return a matrix compose by every possible chunk made by contiguous sentences.
        The algorithm is designed to work with aligned texts. See the results of 02.2c-Jaccard-Align-Preproc-to-Original-Sent.ipynb
        """
        self.fragMatrix = DataFrame([])
        
        if textName.startswith('susp'): column = 'susp'
        else: column = 'src'
        
        #Load aligned text structure corresponding to doc = idTrueCase
        alignedText = pd.read_csv(os.path.join('../align',column,self.TextPairs[column][idx]),
                         names=['id','sent','offset','length'], 
                         sep='\t')

        #Generate de chunk matrix
        for idy in alignedText.index: #for every sentence
            fragVector = []
            fragment = ''
            for x in range(len(alignedText)):
                if x >= idy:
                    fragment += str(alignedText['sent'][x]) + ' '
                    fragVector.append(fragment)
                else: fragVector.append('NaN')
            self.fragMatrix[idy]=fragVector
        
        return self.fragMatrix

    def getFeatureVector(self, frag):
        """Calc shallow similarity between a text fragment and every chunk generated in :func: getFragFrom.
        This implementation could be changed and is based on:
        * length, whitespaces count, and sentence count
        Return: a vector with the feature score for every chunk generated in :func: getFragFrom.
        """
        self.featureFragMatrix = DataFrame([])
        F1f = len(frag)
        for x in self.fragMatrix.index:
            FValue_Vector = []
            for y in self.fragMatrix.xs(x).index:
                F1 = len(self.fragMatrix[y][x])
                #print(F1,F1f)
                F1v = pow(F1*F1f,1/2)/float(sum([F1,F1f]))
                #print(F1v)
                F2v = calcCommonWords(frag,self.fragMatrix[y][x])
                #print(F2v)
                FValue = pow(F1v*F1v*F2v,1)/float(sum([F1v,F1v,F2v]))
                #print(FValue)
                #input()
                FValue_Vector.append(FValue)
            self.featureFragMatrix[x] = FValue_Vector
        return self.featureFragMatrix

    def bestValue(self):
        """Return best chunk of susp/src DOC """
        maxv = 0; xmax = 0; ymax = 0
        for idx in self.featureFragMatrix.columns:
            for idy in self.featureFragMatrix[idx].keys():

                if self.featureFragMatrix[idx][idy] > maxv:
                    maxv = self.featureFragMatrix[idx][idy]
                    xmax = idx;ymax = idy
        return xmax,ymax

def appendCorpusCase(newCaseID, bestEval):
    """Write the positive cases corpus
    """
    #TODO: send CorpusName as a parameter
    
    paraphCorpus = open(outdir+'/PAN-None-Paraphrase-Corpus','a')
    newCase = newCaseID+'\t'+bestEval['susp']+'\t'+bestEval['src']+'\t'+str(0)+'\n'
    paraphCorpus.write(newCase)
    paraphCorpus.close()

#Function utils
def matrixCommonWords(TextPairs, TrueCases):
    """ Get the common Word Matrix columns = TrueCases, index = textCase.
    """
    
    for idy in TextPairs.index:
        susp = os.path.join(suspdir, TextPairs.susp[idy])
        src = os.path.join(srcdir, TextPairs.src[idy])

        wordSusp = set(open(susp).read().split())
        wordSrc = set(open(src).read().split())

        CW_Vector = []
        
        for idx in TrueCases.index:
            CW_Vector.append(calcCommonWords(TrueCases.xs(idx),wordSusp,wordSrc))
        
        CWM[idy] = CW_Vector

    #save CWM into a file for future uses
    col = [x for x in range(0,len(TextPairs))]
    CWM.to_csv(path_or_buf='CWM.csv',cols=col)

    return CWM

def calcCommonWords(wordSusp, wordSrc,trueCase = False):
    "Get similarity between vocabularies."
    if trueCase:
        U = set(trueCase['suspf'].split())
        T = set(trueCase['srcf'].split())
        Q = wordSusp
        R = wordSrc
        return len(Q.intersection(U))/float(len(U))+len(R.intersection(T))/float(len(T))
    else:
        U = set(wordSusp.split())
        T = set(wordSrc.split())
        Q = wordSusp
        R = wordSrc
        return len(T.intersection(U))/float(len(U.union(T)))




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
        except:
            pass

        #Start the process
        pipeline.loadCWMatrix(CWM)
        pipeline.bestNTextsPerTrueCase()
        pipeline.getFalseCases()

    else:
        print('\n'.join(["Unexpected number of commandline arguments.",
                         "Usage: ./02.3_alignNormalizedCaseList.py {Non-pairs} {True-pairs} {src-dir} {susp-dir} {out-dir}"]))
    timef = time.time() - initt
    print ('tiempo total: ',timef)
