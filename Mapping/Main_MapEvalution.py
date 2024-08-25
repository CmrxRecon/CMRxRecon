#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 26 22:08:22 2023

"""

import os
import numpy as np
from loadFun import loadmat, kdata2img, multicoilkdata2img
import sys
from Evaluation import calmetric, save_metric, memo_metric0, save_df
from CalEvalMap import CalSaveT2map, EvalMyo, CalSaveT1map
Task_Type = 'Mapping'

'''
============ You need to upload the data (download from CMRxRecon challenge) ===========
'''
Coil_Type = input("Please enter 'SingleCoil' or 'MultiCoil': ")
if Coil_Type != 'SingleCoil' and Coil_Type != 'MultiCoil':
    print("Input error! Only 'SingleCoil' or 'MultiCoil' are allowed")
    sys.exit()
user_input = input("Please enter 'T1' or 'T2': ")
if user_input == "T1":
    Sub_Task = 'T1map'
elif user_input == "T2":
    Sub_Task = 'T2map'
else:
    print("Input error! Only 'T1' or 'T2' are allowed")
    sys.exit()

Recon_dir = 'AccFactor04'
data_base = '/Users/apple/Documents/CMR-Challenge/Demo_ChallengeData/'
'''======================================================================================
'''
# Directory of the file to be compared
target_dir = os.path.join(data_base, Coil_Type, Task_Type, 'TestSet', Recon_dir)

# Directory of the reference file
gt_dir = os.path.join(data_base, Coil_Type, Task_Type, 'TestSet', 'FullSample')
seg_dir = os.path.join(data_base, Coil_Type, Task_Type, 'TestSet', 'SegmentROI')

# Getting a list of all folders to be compared
target_folders = sorted(os.listdir(target_dir))
gt_folders = sorted(os.listdir(gt_dir))
seg_folders = sorted(os.listdir(seg_dir))

table = []
processed_list = []

PSNR_list = []
SSIM_list = []
NMSE_list = []
# traversing through a folder and calculating the metric value
for folder in gt_folders:
    target_path = os.path.join(target_dir, folder, Sub_Task + '.mat')
    reference_path = os.path.join(gt_dir, folder, Sub_Task + '.mat')
    invtime_path = os.path.join(gt_dir, folder, Sub_Task + '.csv')
    seg_path = os.path.join(seg_dir, folder, Sub_Task + '_label.nii.gz')
    if os.path.exists(target_path) and os.path.exists(reference_path) and os.path.exists(seg_path):
        target_data = loadmat(target_path)
        reference_data = loadmat(reference_path)
        if Coil_Type == 'SingleCoil':
            pred_recon = kdata2img(target_data)
            gt_recon = kdata2img(reference_data)
        else:
            pred_recon = multicoilkdata2img(target_data)
            gt_recon = multicoilkdata2img(reference_data)

        if Sub_Task == 'T2map':
            T2ReconMap = CalSaveT2map(pred_recon, invtime_path, target_dir, folder)
            T2GTMap = CalSaveT2map(gt_recon, invtime_path, gt_dir, folder)
            df = EvalMyo(T2ReconMap, seg_path, 'T2')
            line = df['Mapping'].values
            table += [line]
            processed_list += [folder]
            [psnr_array, ssim_array, nmse_array] = calmetric(T2ReconMap, T2GTMap)
        else:
            T1ReconMap = CalSaveT1map(pred_recon, invtime_path, target_dir, folder)
            T1GTMap = CalSaveT1map(gt_recon, invtime_path, gt_dir, folder)
            df = EvalMyo(T1ReconMap, seg_path, 'T1')
            line = df['Mapping'].values
            table += [line]
            processed_list += [folder]
            [psnr_array, ssim_array, nmse_array] = calmetric(T1ReconMap, T1GTMap)
    elif not os.path.exists(target_path) and os.path.exists(reference_path):
        print(target_path + ' is missing! Please check!')
        reference_data = loadmat(reference_path)
        gt_recon = kdata2img(reference_data)
        [psnr_array, ssim_array, nmse_array] = memo_metric0(gt_recon)
    else:
        continue

    PSNR_list.append(psnr_array.reshape(1, -1))
    SSIM_list.append(ssim_array.reshape(1, -1))
    NMSE_list.append(nmse_array.reshape(1, -1))
    save_metric(psnr_array, ssim_array, nmse_array, folder, Sub_Task,Coil_Type)
    save_df(user_input, table, processed_list, Sub_Task, Coil_Type)

psnr_results = np.mean(np.concatenate(PSNR_list, axis=1))
ssim_results = np.mean(np.concatenate(SSIM_list, axis=1))
rmse_results = np.mean(np.concatenate(NMSE_list, axis=1))

print('Mean PSNR:', (psnr_results))
print('Mean SSIM:', (ssim_results))
print('Mean NMSE:', (rmse_results))

print('All checked!')
