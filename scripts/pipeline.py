#!/usr/bin/env python 3.6
# -*- coding: utf-8 -*- 

"""Auxiliar class definition to make short the original script's code.
"""

import os
from preprocess.demo import preProcessFlow as textNormalizationProcess

class Process:
    def __init__(self, susp, src, outdir, docDict, stepFunc):
        """
        :param stepFunc: function that transform a txt collection sequentially

        In 2019 version this func can be only = textNormalizationProcess or
                                                alignSentences
        """
        self.susp = susp
        self.src = src
        self.susp_file = os.path.split(susp)[1]
        self.src_file = os.path.split(src)[1]
        self.outdir=outdir
        self.validProcess = []
        self.docDict = docDict
        self.stepFunc = stepFunc
        self.filepath = ['susp/','src/']

    def process(self):

        validProcess = []
        for i,fileName in enumerate([self.susp, self.src]):
        	#Normalize if you didn't before
            if fileName not in self.docDict.keys():
                validProcess = self.preprocess(fileName,i)
            #Don't normalize again, take the value obtained before
            else:
                validProcess = self.docDict[fileName]

            self.validProcess.append(validProcess)

        return self.validProcess

    def preprocess(self, fileName, i):
        """ Text pipeline. """

        #Load original text
        with open(fileName) as _file:
            original_text = _file.read()
        
        if self.stepFunc == textNormalizationProcess:
            #Normalizing Text
            text_result = self.stepFunc(original_text)

            #write the preprocessed text in a new path with the same name
            doc = open(self.outdir+self.filepath[i]+os.path.split(fileName)[1],'w')
            doc.write(text_result)
            doc.close()
        
        else:
            #Load normalized text
            with open('data/norm/'+self.filepath[i]+os.path.split(fileName)[1]) as _file:
                normalized_text = _file.read()
            
            #Align text with its original
            aligned_sents = self.stepFunc(normalized_text, original_text)

            #Write the obtained structure in a text file
            alignedDoc = open(self.outdir+self.filepath[i]+os.path.split(fileName)[1],'w')
            for sent in aligned_sents:
                alignedDoc.write(str(sent[0])+'\t'+sent[1]+'\t'+str(sent[2])+'\t'+str(sent[3])+'\n')
            alignedDoc.close()

        # else:
        #     print("The function ", self.stepFunc, " it is not available.""")
        #     return False

        return True