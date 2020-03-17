#!/usr/bin/env python 3.5
# -*- coding: utf-8 -*- 

from .corpusReader import PANXml_Reader
from .datasets import msrpc_to_csv, msrpc_to_arff, load_msrpc
from .parallel import parallel_process, return_obj