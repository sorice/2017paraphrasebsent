#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

"""Script for 
Created on Thu Nov 03 2016
Modified by analysis on:  
Finish on: 
.. version: 0.1
.. release: 0.1-RC1
.. author: Abel Meneses abad
"""
import os
from IPython.display import display
from IPython.display import (
    display_html, display_jpeg, display_png,
    display_javascript, display_svg, display_latex
)

from xml.dom.minidom import parse
import xml.dom.minidom

class PANXml_Reader:
    """Class to work with plagiarism PAN XML document using minidom parser."""

    def __init__ (self, xmlFileName):
        self.xmlFileName = xmlFileName
        self.fragmentList = []

    def parser(self):
        """Parse one XML document of PAN Plagiarism XML corpus."""
    
        DOMTree = xml.dom.minidom.parse(self.xmlFileName)
        rootElement = DOMTree.documentElement
        self.cases = rootElement.getElementsByTagName('feature')
        
        plagDocumentName = rootElement.getAttribute('reference')
        for _ in self.cases:
            suspDoc = plagDocumentName
            srcDoc = _.getAttribute("source_reference")
            susp_offset = _.getAttribute("this_offset")
            susp_len = _.getAttribute("this_length")
            src_offset = _.getAttribute("source_offset")
            src_len = _.getAttribute("source_length")
            paraph = _.getAttribute("obfuscation")
            
            caso = pairCase(suspDoc, srcDoc, susp_offset, susp_len, src_offset, src_len, paraph)
            
            self.fragmentList.append(caso)
            
        return self.fragmentList

class pairCase(object):
    def __init__(self, suspDocName, srcDocName, susp_offset, susp_len, src_offset, src_len, paraph):
        self.suspDocName = suspDocName
        self.srcDocName = srcDocName
        self.suspOffset = susp_offset
        self.srcOffset = src_offset
        self.suspLength = susp_len
        self.srcLength = src_len
        self.paraph = paraph

def constructHTML(text1, text2):
    struct = '''<table width='400' cellpadding='4' cellspacing='0'>
        <col width='128*'>
        <col width='128*'>
        <tr valign='top'>
            <td width='45*'>
                <p><b>Susp</b></p>
            </td>
            <td width='45*'>
                <p><b>Src</b></p>
            </td>
        </tr>
        <tr valign='top'>
            <td width='45*'>
                <p> %s </p>
            </td>
            <td width='45*'>
                <p> %s </p>
            </td>
        </tr>
    </table>'''
    
    return struct % (text1,text2)


def getText(docname, offset, length):
    doc = open(docname).read()
    fragment = doc[int(offset):int(offset)+int(length)]
    return fragment 

class Tabla(object):
    def __init__(self,code):
        self.struct = code
    def _repr_html_(self):
        return self.struct

def Flow():
    xmlPATH = 'data/orig/xml/'
    textPATH = 'data/orig/'
    pair = PANXml_Reader(os.path.abspath(xmlPATH+'suspicious-document00007-source-document00382.xml'))
    case  = pair.parser()
    text1 = getText(textPATH+'susp/'+case[0].suspDocName, case[0].suspOffset,case[0].suspLength)
    text2 = getText(textPATH+'src/'+case[0].srcDocName, case[0].srcOffset,case[0].srcLength)
    struct = constructHTML(text1, text2)
    tabla = Tabla(struct)
    display_html(tabla)

    return

if __name__ == "__main__":
    Flow()
