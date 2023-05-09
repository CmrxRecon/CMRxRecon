#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed April 10 00:20:05 2023
Load .mat data using python

@author: c.y.wang
"""


import os
#import numpy as np
from loadFun import loadmat

data_dir = 'data'
mat_file = os.path.join(data_dir, 'example.mat')

data = loadmat(mat_file)
