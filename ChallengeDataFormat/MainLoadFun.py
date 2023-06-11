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

# Load mat
data_dir = 'data'
mat_file = os.path.join(data_dir, 'example.mat')

data = loadmat(mat_file)

# write mat
# Create the MATLAB data file
mat_file = h5py.File('data.mat', 'w')

# Save the data to the file
mat_file.create_dataset('data', data= mat_file)  # Create dataset and save data
# Replace 'mat_file' with the desired dataset name

# Close the file
mat_file.close()