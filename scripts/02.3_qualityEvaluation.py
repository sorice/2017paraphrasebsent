#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Script for 
Created on Thu Nov 03 2016
Modified by analysis on:  
Finish on: 
.. version: 0.1
.. release: 
.. author: Abel Meneses abad
"""


class pairCase(object):
    def __init__(self, suspDocName, srcDocName, susp_offset, susp_len, src_offset, src_len):
        self.suspDocName = suspDocName
        self.srcDocName = srcDocName
        self.suspOffset = susp_offset
        self.srcOffset = src_offset
        self.suspLength = susp_len
        self.srcLength = src_len

#IN: lista de casos (pair file)

#Leer todos los textos con formato

#OUT: lista de tuplas (id, doc1, sent1, offset1, len1, %inside_fragment, previously_checked)

if __name__ == "__main__":
    Flow()
