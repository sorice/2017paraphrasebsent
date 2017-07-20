#!/usr/bin/env pythonS3.5
# -*- coding: utf-8 -*-

"""Utilitie functions to standarize the IN-object to the preprocessing method.
If the user enter a path to preprocess a list of document, or a doc the module will no fail.
Created on Wed Nov 09 2016
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
from preprocess.methods import add_text_end_dot, abbrev_recognition_support 
from preprocess.methods import contiguos_string_recognition_support, del_contiguous_point_support
import os

def alignSentences(preproc_text, original_text):
    """Align preprocessed sentences vs original sentences returning the original boundaries.
    Useful for real applications, to recover the original sentence position or fragment position
    and show in a web or desktop application view.

    :param preproc_text: preprocessed text string
    :param original_text: original text string
    :returns alignedSentences: [(sent ID, preprocessed sentence, offset original sent, length orig sent)]
    :rtype: list of tuples

    .. author: Abel Meneses abad
    Finish on Fri, 9 Sept 2016
    Next_revision on (an Optimization is predicted)
    """
    alignedSentences = []
    offsetB = 0
    norm_orig_text = normalize(original_text)

    #if norm_orig_text.count('.') < preproc_text.count('.'):
     #   raise Exception("Preprocess Error: number of preproc periods most be less or equal than normalize original text periods.")

    for i, (sentA, offsetA, lengthA) in enumerate(getSentA(preproc_text)):
        maxScore =-1; score = 0
        prevPoint = 0#len(sentA)-2
        nextPoint = 0
        iqualScore = 0;prevFrag='';jaccard_measure = 0; X = {()}; Y={()}
        prev_jaccard_measure = 1.0
        k = 0.5

        if len(sentA) > 200:
             k = 0.1
        else: k=0.5
        
        #Sí llegamos a la última oración entonces
        if i == preproc_text.count('.')-1:
            lengMax = len(norm_orig_text)
            tuple = (i, sentA, offsetB, lengMax)
            alignedSentences.append(tuple)
            break
        
        #Sí no es la última oración compara hasta encontrar el score max.
        while(score >= maxScore):
            prev_jaccard_measure = jaccard_measure; prev_setA = X; prev_setB = Y
            lengMax = nextPoint
            maxScore = score
            
            #Get sentence B and prepare it to calc distances
            sentB, nextPoint, prevPoint = getSentB(norm_orig_text, offsetB, nextPoint, prevPoint)
            sentB = sentB.replace('\n',' ') #avoid some bugs on swalign function
            
            #Calc distances Jaccard
            jaccard_measure, X, Y = jaccard ( sentA , sentB) #Second measure only to lookfor errors
            score = jaccard_measure
 
            #The same consecutives sentence exception
            if prevFrag == sentB[-round(len(sentA)*k):]:
                break
            prevFrag = sentB[-round(len(sentA)*k):] #keep the previous fragment to know if the next sent is the same as before. SmithWaterman move forward to the next sentence.

            #Short sentence exceptions
            if len(sentA) < 14:
                maxScore = score
                lengMax = nextPoint
                break

            #Infinite loop exception
            if score == maxScore:
                iqualScore += 1
            if iqualScore == 20:
                break

        tuple = (i, sentA, offsetB, lengMax)
        alignedSentences.append(tuple)

        offsetB = lengMax

    return alignedSentences

def getSentA(doc1):
    offset = 0
    for i in re.finditer('\.',doc1):
        sentA = doc1[offset:i.end()]
        yield sentA, offset, i.end()
        offset = i.end()+1

def getSentB(text2, offsetB, nextPoint,sentLength):
    posB = text2[offsetB+sentLength:].find('.')
    sentLength += posB+1
    sentB = text2[offsetB:offsetB+sentLength]
    nextPoint = offsetB + sentLength
    return sentB, nextPoint, sentLength

def normalize(text_orig):
    replacement_patterns = [(r'[:](?=\s*?\n)','##1'),
                            (r'\xc2|\xa0',' '),
                            (r'(\w\s*?):(?=\s+?[A-Z]+?)|(\w\s*?):(?=\s*?"+?[A-Z]+?)','\g<1>##2'),
                            (r'[?!]','##3'),
                            (r'(\w+?)(\n)(?=["$%()*+&,-/;:¿¡<=>@[\\]^`{|}~\t\s]*(?=.*[A-Z0-9]))','\g<1>##4'), # any alphanumeric char
                            # follow by \n follow by any number of point sign follow by a capital letter, replace by alphanumerig+.
                            (r'(\w+?)(\n)(?=["$%()*+&,-/;:¿¡<=>@[\\]^`{|}~\t\s\n]*(?=[a-zA-Z0-9]))','\g<1>##5'),# any alphanumeric char
                            # follow by \n follow by any number of point sign follow by a letter, replace by alphanumerig+.
                            (r'[:](?=\s*?)(?=["$%()*+&,-/;:¿¡<=>@[\\]^`{|}~\t\s]*[A-Z]+?)','##6'),
                            (r'(\w+?\s*?)\|','\g<1>##7'),
                            (r'\n(?=\s*?[A-Z]+?)','##8'),
                            (r'##\d','apdbx'),
                            ]
    
    for (pattern, repl) in replacement_patterns:
            (text_orig, count) = re.subn(pattern, repl, text_orig)
    
    text_orig = del_contiguous_point_support(text_orig)
    text_orig = contiguos_string_recognition_support(text_orig)
    text_orig = abbrev_recognition_support(text_orig)
    text_orig = re.sub(r'apdbx+','.', text_orig)
    text_orig = add_text_end_dot(text_orig)#append . final si el último caracter no tiene punto, evita un ciclo infinito al final.
    return text_orig

def jaccard(text1,text2):
    sentA1 = re.sub(r'[!"#$%&()\'*+,-/:;<=>?@\\^_`{|}~.\[\]]',' ', text1)
    sentB1 = re.sub(r'[!"#$%&()\'*+,-/:;<=>?@\\^_`{|}~.\[\]]',' ', text2)
    setA = set(sentA1.split())
    setB = set(sentB1.split())
    if len(setA.union(setB)) == 0:
        return 0, sentA1, sentB1
    else:
        return len(setA.intersection(setB))/float(len(setA.union(setB))), sentA1, sentB1

class ProcessCase:
    def __init__(self, susp, src, outdir, alignedDocList):
        self.susp = susp
        self.src = src
        self.susp_file = os.path.split(susp)[1]
        self.src_file = os.path.split(src)[1]
        self.outdir=outdir
        self.validText = True
        self.validProcess = []
        self.alignedDocList = alignedDocList
        self.path=['susp/','src/']

    def process(self):
        validProcess = []
        for i,fileName in enumerate([self.susp, self.src]):
            if fileName not in self.alignedDocList.keys():
                validProcess = self.preprocess(fileName,i)
            else:
                validProcess = self.alignedDocList[fileName]

            self.validProcess.append(validProcess)

        return self.validProcess

    def preprocess(self, fileName,i):
        """ Text normalization pipeline. """
        
        #Load original text
        with open(fileName) as _file:
            original_text = _file.read()
        
        #Load normalized text
        with open('../norm/'+self.path[i]+os.path.split(fileName)[1]) as _file:
            normalized_text = _file.read()
        
        #Alinear texto con su original
        aligned_sents = alignSentences(normalized_text, original_text)

        #Write the obtained structure in a text file
        alignedDoc = open('../align/'+self.path[i]+os.path.split(fileName)[1],'w')
        for sent in aligned_sents:
            alignedDoc.write(str(sent[0])+'\t'+sent[1]+'\t'+str(sent[2])+'\t'+str(sent[3])+'\n')
        alignedDoc.close()

        return self.validText

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
        alignedDocList = {}
        validCases = []

        txt = open(outdir+'alignedDocList')
        doc = txt.read()
        for line in doc.split('\n'):
            if line[line.find(' ')+1:] == 'True':
                alignedDocList[line[:line.find(' ')]] = True
            else:
                if len(line) > 1:
                    alignedDocList[line[:line.find(' ')]] = False
        txt.close()

        for i,line in enumerate(lines):
            susp, src = line.split()
            if len(susp) > 1:
                flow = ProcessCase(os.path.join(suspdir, susp),
                                    os.path.join(srcdir, src), outdir,
                                    alignedDocList)

                validProcess = flow.process()
                result = validProcess[0]&validProcess[1]

                #if result is good then the text pairs contain in line is valid
                #then write a valid case
                if result: 
                    positive+=1
                    validCases.append(line[:-1])
                    
                #update alignedDocList
                alignedDocList[os.path.join(suspdir, susp)] = validProcess[0]
                alignedDocList[os.path.join(srcdir, src)] = validProcess[1]
                
                if i*10%cases <= 10 or i == len(lines)-1:
                    print(i+1,'/',cases,'TRUE:', positive)

        #write valid cases in a text
        pairValidDoc = open(outdir+'align_pairs','w')
        for case in validCases:
            pairValidDoc.write(case+'\n')
        pairValidDoc.close()

        #write pre processed doc list in a text to avoid future re-preprocessing
        doc = open(outdir+'alignedDocList','w')
        for key,value in alignedDocList.items():
            doc.write(key+' '+str(value)+'\n')
        doc.close()

    else:
        print('\n'.join(["Unexpected number of commandline arguments.",
                         "Usage: ./02.3_alignNormalizedCaseList.py {pairs} {src-dir} {susp-dir} {out-dir}"]))
    timef = time.time() - initt
    print ('tiempo total: ',timef)