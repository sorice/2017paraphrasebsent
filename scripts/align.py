#!/usr/bin/env python 3.6
# -*- coding: utf-8 -*- 

from preprocess.normalize import add_doc_ending_point, abbreviations
from preprocess.normalize import multipart_words, replace_point_sequence
from preprocess.normalize import expand_contractions, replace_symbols
import re

def getNormSent(text1):
    offset = 0
    for i in re.finditer('\.',text1):
        sentA = text1[offset:i.end()]
        yield sentA, offset, i.end()
        offset = i.end()+1

def BasicNormalization(text_orig):
    norm_text = text_orig
    replacement_patterns = [(r'\n',' '),
                            (r'[?!]','.'),
                            (r'["$%()*+&#\',-/;:¿¡<=>@\\^`{\|}~]|\[|\]',' '),
                            ]
    
    for (pattern, repl) in replacement_patterns:
            (text_orig, count) = re.subn(pattern, repl, norm_text)
    
    norm_text = replace_point_sequence(norm_text)
    norm_text = multipart_words(norm_text)
    norm_text = abbreviations(norm_text)
    norm_text = add_doc_ending_point(norm_text)
    
    if len(norm_text) > len(text_orig)+2:
        raise ValueError ('Basic normalization change the length of original sentence')

    return norm_text

def jaccard(normText,origText):
    #Where simbols means more words and additional length
    origText = re.sub(r'’','\'',origText)
    origText = expand_contractions (origText,lang='en')
    origText = re.sub(r'(\w+?)-\n(?=[a-z]+?)','  \g<1>', origText)
    origText = replace_symbols (origText)
    sentB1 = re.sub(r'[\W_]',' ', origText)
    sentListA = normText.split()
    sentListB = sentB1.split()
    A = set(sentListA)
    B = set(sentListB)
    C = len(sentListA)
    D = len(sentListB)
        
    if A.symmetric_difference(B) == set() and C==D and sentB1.endswith(' '):
        return 1.0
    else:
        return 0.5

def getOrigSent(text2, offsetB, lenB,windows = 1):
    sentB = text2[offsetB:offsetB+lenB]
    lenB += windows
    return sentB, lenB

def sentenceAligner(preproc_text, original_text):
    """Align preprocessed sentences vs original sentences based on sliding window

    Created on  Sept 2019
    .. author: Abel Meneses abad
    """

    alignedSentences = []
    offsetB = 0
    norm_orig_text = BasicNormalization(original_text)
    number_of_sentences = preproc_text.count('.')
        
    for i, (sentA, _ , _ ) in enumerate(getNormSent(preproc_text)):
        maxScore =-1; score = 0
        
        #Delete any non alphanumeric char to get the words
        sentA = re.sub(r'[\W_]',' ', sentA)
        
        #Empty SentA
        if len(sentA.split()) == 0:
            prevLenB = len(sentA)-2
            

        else:

            #Deduct:
            #-1 for 0 list start 
            #-1 for ' ' added before point in normalization
            #-5 the bigger # of chars added by expand_contractions func
            if offsetB > 10:
                lenB = len (sentA) - 10 
            else:
                lenB = len(sentA) -3
        
            iqualScore = 0
            prevFrag=''
            jaccard_measure = 0
            prev_jaccard_measure = 1.0
            k = 0.5
            
            #Sí llegamos a la última oración entonces
            if i == number_of_sentences - 1: 
                lenB = len(norm_orig_text) - offsetB
                tuple = (i, sentA, offsetB, lenB)
                alignedSentences.append(tuple)
                break
            
            #Sí no es la última oración compara hasta encontrar el score max.
            while(score >= maxScore):
                prevLenB = lenB
                prev_jaccard_measure = jaccard_measure #for print, del when works
                maxScore = score
                
                #Get original Sentence and prepare it to calc distances
                sentB, lenB = getOrigSent(norm_orig_text, offsetB, lenB, windows = 1)
                    
                #Calc measures Jaccard
                jaccard_measure = jaccard ( sentA , sentB)
                
                score = jaccard_measure
                    
                #Infinite loop exception
                if score == maxScore:
                    iqualScore += 1
                if iqualScore == 500:
                    raise ValueError('The same score repeated to many times, not possible!')
            
        tuple = (i, sentA, offsetB, prevLenB-1)
        alignedSentences.append(tuple)
        
        offsetB = offsetB+prevLenB-1

    return alignedSentences 

class alignedText(object):
    """Aligned texts are very useful objects with complex structure.
    This class implement methods to access them.
    """
    def __init__(self, docName, dataPath = 'data/aligned/'):
        self.docName = docName
        self.dataPath = dataPath
        self.sentList = list(tuples())
        self.TextFragment = ''

    def readAligned(self):
        """Read the structure of an aligned text."""
        with open(self.dataPath+self.docName) as doc:
            for line in doc:
                self.sentlist.append(tuple(line.split('\t')))
        return self.sentList

    def getTextFragment(self,offset,length):
        for sent in self.sentList:
            frag = int(sent[2])+int(sent[3])
            if frag > offset and frag < offset + length:
                self.TextFragment += sent[1]+' '
            else:
                pass
        return self.TextFragment