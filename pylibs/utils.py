#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

"""Utilitie functions to prepare the data.
If the user enter a path to preprocess a list of document, or a doc the module will no fail.
Created on Oct XX 2016
Modified by analysis on 
Finish on 
.. version: 0.1
.. release: 0.1-RC1
.. author: Abel Meneses abad
"""

import sys
sys.path.append('/home/abelm')
import re
from preprocess.methods import add_text_end_dot, abbrev_recognition_support 
from preprocess.methods import contiguos_string_recognition_support, del_contiguous_point_support
import time
import os
from preprocess.example import preProcessFlow as textNormalizationProcess

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

    for i, (sentA, offsetA, lengthA) in enumerate(getSentA(preproc_text)):
        
        maxScore =-1; score = 0
        prevPoint = 0#len(sentA)-2
        nextPoint = 0
        iqualScore = 0;prevFrag='';jaccard_measure = 0; X = {()}; Y={()}
        prev_jaccard_measure = 1.0
        k = 0.5

        #Sí llegamos a la última oración entonces
        if i == preproc_text.count('.')-1:
            lengMax = len(norm_orig_text)
            tuple = (i, sentA, offsetB, lengMax, prev_jaccard_measure)
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
            #alignment = sw.align(sentA[-round(len(sentA)*k):], sentB[-round(len(sentA)*k):])
            jaccard_measure, X, Y = jaccard ( sentA , sentB) #Second measure only to lookfor errors
            score = jaccard_measure
 
            #Repeated sentence exception src00014
            if prevFrag == sentB[-round(len(sentA)*k):]:
                break
            prevFrag = sentB[-round(len(sentA)*k):] #keeping the obtained frag to the next round.

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

        tuple = (i, sentA, offsetB, lengMax, prev_jaccard_measure)
        alignedSentences.append(tuple)

        if prev_jaccard_measure < 0.7 and prev_jaccard_measure > 0.0:
            print ('jaccard_measure:',prev_jaccard_measure)
            #print (prev_setA,'<--->',prev_setB)
            print('#############RESULTADO de la ORACIÓN :', i)
            print('score max:',maxScore, 'offsetB:', offsetB, 'lengthB:',lengMax-offsetB)
            print('sentB:',original_text[offsetB:lengMax])
            print('sentA:',sentA)
            print('\n***************')

        offsetB = lengMax

    return alignedSentences

def getSentA(doc1):
    offset = 0
    for i in re.finditer('\.',doc1):
        sentA = doc1[offset:i.end()]
        yield sentA, offset, i.end()
        offset = i.end()+1

def getSentB(text2, offsetB, nextPoint,prevPoint):
    posB = text2[offsetB+prevPoint:].find('.')
    prevPoint += posB+1
    sentB = text2[offsetB:offsetB+prevPoint]
    nextPoint = offsetB + prevPoint
    return sentB, nextPoint, prevPoint

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

class Process:
    def __init__(self, susp, src, outdir, preProcessedDocList):
        self.susp = susp
        self.src = src
        self.susp_file = os.path.split(susp)[1]
        self.src_file = os.path.split(src)[1]
        self.outdir=outdir
        self.validText = True
        self.validProcess = []
        self.preProcessedDocList = preProcessedDocList
        self.filepath = ['susp/','src/']

    def process(self):
        validProcess = []
        for i,fileName in enumerate([self.susp, self.src]):
            if fileName not in self.preProcessedDocList.keys():
                validProcess = self.preprocess(fileName,i)
            else:
                validProcess = self.preProcessedDocList[fileName]

            self.validProcess.append(validProcess)

        return self.validProcess

    def preprocess(self, fileName, i):
        """ Text normalization pipeline. """
        with open(fileName) as _file:
            text = _file.read()
        
        #Normalizar texto
        textNorm = textNormalizationProcess(text)
        #~ print('text normalization done')
        
        #Alinear texto con su original
        textAlignedSents = alignSentences(textNorm, text)
        #~ print('text alignment done')

        #Analizar la columna con los valores de jaccard
        #Por experimentación sabemos que sí hay valores entre > 0 y < 0.7
        #ents. el alineamiento tiene problemas.
        textJaccardCoefList = [textAlignedSents[i][4] for i in range(len(textAlignedSents))]

        for element in textJaccardCoefList:
            if element >0 and element < 0.3:
                self.validText = False
                self.preProcessedDocList[fileName] = False # Add fileName to preprocessed doc list
            
            if self.validText:
                self.preProcessedDocList[fileName] = True # Add fileName to preprocessed doc list
                doc = open(self.outdir+self.filepath[i]+os.path.split(fileName)[1],'w') #write the preprocess text result
                doc.write(textNorm); doc.close()

        return self.validText

if __name__ == "__main__":
    """ Process the commandline arguments. We expect three arguments: The path
    pointing to the pairs file and the paths pointing to the directories where
    the actual source and suspicious documents are located.
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
                normalizedDocList[line[3:line.find(' ')]] = True
            else:
                if len(line) > 1:
                    normalizedDocList[line[3:line.find(' ')]] = False
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
                    
                #update normalizedDocList
                normalizedDocList['susp/'+susp] = validProcess[0]
                normalizedDocList['src/'+src] = validProcess[1]
                    
                print(i,'/',cases, positive, 'TRUE')
            
            except: #blank lines for example
                print(i,'/',cases, positive, 'FALSE')
            
        #write valid cases in a text
        pairValidDoc = open(outdir+'norm_pairs_utils','w')
        for case in validCases:
            pairValidDoc.write(case+'\n')
        pairValidDoc.close()
        
        #write pre processed doc list in a text to avoid future re-preprocessing
        doc = open(outdir+'normalizedDocList','w')
        for key,value in normalizedDocList.items():
            doc.write('../'+key+' '+str(value)+'\n')
        doc.close()

    else:
        print('\n'.join(["Unexpected number of commandline arguments.",
                         "Usage: ./utils.py {pairs} {src-dir} {susp-dir} {out-dir}"]))
    timef = time.time() - initt
    print ('tiempo total: ',timef)