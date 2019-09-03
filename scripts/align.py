#!/usr/bin/env python 3.6
# -*- coding: utf-8 -*- 

from preprocess.normalize import add_doc_ending_point, abbreviations 
from preprocess.normalize import multipart_words, replace_point_sequence
import re

def getSentA(text1):
    offset = 0
    for i in re.finditer('\.',text1):
        sentA = text1[offset:i.end()]
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
    
    text_orig = replace_point_sequence(text_orig)
    text_orig = multipart_words(text_orig)
    text_orig = abbreviations(text_orig)
    text_orig = re.sub(r'apdbx+','.', text_orig)
    text_orig = add_doc_ending_point(text_orig)#append . final si el último caracter no tiene punto, evita un ciclo infinito al final.
    return text_orig

def __jaccard(text1,text2):
    sentA1 = re.sub(r'[!"#$%&()\'*+,-/:;<=>?@\\^_`{|}~.\[\]]',' ', text1)
    sentB1 = re.sub(r'[!"#$%&()\'*+,-/:;<=>?@\\^_`{|}~.\[\]]',' ', text2)
    setA = set(sentA1.split())
    setB = set(sentB1.split())
    total_terms = len(sentB1.split())
    return len(setA.intersection(setB))/(total_terms or 1)

def sentenceAligner(preproc_text, original_text):
    """Align preprocessed sentences vs original sentences returning the original boundaries.
    Useful for real applications, to recover the original sentence position or fragment position
    and show in a web or desktop application view.

    :param preproc_text: preprocessed text string
    :param original_text: original text string
    :returns alignedSentences: [(sent ID, preprocessed sentence, offset original sent, length orig sent)]
    :rtype: list of tuples

    Created on  Sept 2016
    .. author: Abel Meneses abad
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
        iqualScore = 0
        prevFrag=''
        jaccard_measure = 0
        k = 0.5

        #Optimization for long sentences
        if len(sentA) > 200:
             k = 0.1
        else: k=0.5
        
        #If arrive to the last sentence
        if i == preproc_text.count('.')-1:
            lengMax = len(norm_orig_text)
            tuple = (i, sentA, offsetB, lengMax)
            alignedSentences.append(tuple)
            break
        
        #If not the last sent then continue
        while(score >= maxScore):
            lengMax = nextPoint
            maxScore = score
            
            #Get sentence B and prepare it to calc distances
            sentB, nextPoint, prevPoint = getSentB(norm_orig_text, offsetB, nextPoint, prevPoint)
            
            #Calc distances Jaccard
            jaccard_measure = __jaccard( sentA , sentB)
            score = jaccard_measure
 
            #The same consecutives sentence exception
            if prevFrag == sentB[-round(len(sentA)*k):]:
                break
            #keep previous fragment to control if next sent is equal.
            prevFrag = sentB[-round(len(sentA)*k):]

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