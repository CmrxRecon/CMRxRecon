"""
Copyright (c) Facebook, Inc. and its affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""
import os
from typing import Optional
import csv
import pandas as pd

import numpy as np
from skimage.metrics import peak_signal_noise_ratio, structural_similarity


def mse(gt: np.ndarray, pred: np.ndarray) -> np.ndarray:
    """Compute Mean Squared Error (MSE)"""
    return np.mean((gt - pred) ** 2)


def nmse(gt: np.ndarray, pred: np.ndarray) -> np.ndarray:
    """Compute Normalized Mean Squared Error (NMSE)"""
    return np.array(np.linalg.norm(gt - pred) ** 2 / np.linalg.norm(gt) ** 2)


def psnr(
    gt: np.ndarray, pred: np.ndarray, maxval: Optional[float] = None
) -> np.ndarray:
    """Compute Peak Signal to Noise Ratio metric (PSNR)"""
    if maxval is None:
        maxval = gt.max()
    return peak_signal_noise_ratio(gt, pred, data_range=maxval)


def ssim(
    gt: np.ndarray, pred: np.ndarray, maxval: Optional[float] = None
) -> np.ndarray:
    """Compute Structural Similarity Index Metric (SSIM)"""
    if maxval is None:
        maxval = gt.max()
    return structural_similarity(gt, pred, data_range=maxval)


def calmetric(pred_recon, gt_recon):
    if gt_recon.ndim == 4:
        psnr_array = np.zeros((gt_recon.shape[-2], gt_recon.shape[-1]))
        ssim_array = np.zeros((gt_recon.shape[-2], gt_recon.shape[-1]))
        nmse_array = np.zeros((gt_recon.shape[-2], gt_recon.shape[-1]))

        for i in range(gt_recon.shape[-2]):
            for j in range(gt_recon.shape[-1]):
                pred, gt = pred_recon[:, :, i, j], gt_recon[:, :, i, j]
                psnr_array[i, j] = psnr(gt / gt.max(), pred / pred.max())
                ssim_array[i, j] = ssim(gt / gt.max(), pred / pred.max())
                nmse_array[i, j] = nmse(gt / gt.max(), pred / pred.max())
    else:
        psnr_array = np.zeros((1, gt_recon.shape[-1]))
        ssim_array = np.zeros((1, gt_recon.shape[-1]))
        nmse_array = np.zeros((1, gt_recon.shape[-1]))

        for j in range(gt_recon.shape[-1]):
            pred, gt = pred_recon[:, :, j], gt_recon[:, :, j]
            psnr_array[0,j] = psnr(gt / gt.max(), pred / pred.max())
            ssim_array[0,j] = ssim(gt / gt.max(), pred / pred.max())
            nmse_array[0,j] = nmse(gt / gt.max(), pred / pred.max())

    return psnr_array, ssim_array, nmse_array


def save_metric(psnr_array, ssim_array, nmse_array, folder, Sub_Task, Coil_Type):
    Results_folder_name = Coil_Type+'_'+Sub_Task+'_Results'
    if not os.path.exists(Results_folder_name):
        os.makedirs(Results_folder_name)

    filename  = Results_folder_name + '/' + Sub_Task + '_psnr_results.csv'
    if not os.path.isfile(filename):
        with open(filename, mode='a') as psnr_file:
            writer = csv.writer(psnr_file)
            writer.writerow(['folder', 'Sub_Task', 'PSNR'])
    with open(filename, mode='a') as psnr_file:
        writer = csv.writer(psnr_file)
        writer.writerow([folder, Sub_Task, psnr_array])

    filename = Results_folder_name + '/' + Sub_Task + '_ssim_results.csv'
    if not os.path.isfile(filename):
        with open(filename, mode='a') as ssim_file:
            writer = csv.writer(ssim_file)
            writer.writerow(['folder', 'Sub_Task', 'SSIM'])
    with open(filename, mode='a') as ssim_file:
        writer = csv.writer(ssim_file)
        writer.writerow([folder, Sub_Task, ssim_array])

    filename = Results_folder_name + '/' + Sub_Task + '_nmse_results.csv'
    if not os.path.isfile(filename):
        with open(filename, mode='a') as nmse_file:
            writer = csv.writer(nmse_file)
            writer.writerow(['folder', 'Sub_Task', 'NMSE'])
    with open(filename, mode='a') as nmse_file:
        writer = csv.writer(nmse_file)
        writer.writerow([folder, Sub_Task, nmse_array])

def memo_metric0(gt_recon):
    psnr_array = np.zeros((gt_recon.shape[2], gt_recon.shape[3]))
    ssim_array = np.zeros((gt_recon.shape[2], gt_recon.shape[3]))
    nmse_array = np.zeros((gt_recon.shape[2], gt_recon.shape[3]))
    return psnr_array, ssim_array, nmse_array


def save_df(user_input,table,processed_list, Sub_Task,Coil_Type):
    # Save wall thickness for all the subjects
    Results_folder_name = Coil_Type + '_' + Sub_Task + '_Results'
    filename = Results_folder_name + '/' + Sub_Task + '_ROI_results.csv'
    columns_list = ['Mapping_AHA_1', 'Mapping_AHA_2', 'Mapping_AHA_3',
                    'Mapping_AHA_4', 'Mapping_AHA_5', 'Mapping_AHA_6',
                    'Mapping_AHA_7', 'Mapping_AHA_8', 'Mapping_AHA_9',
                    'Mapping_AHA_10', 'Mapping_AHA_11', 'Mapping_AHA_12',
                    'Mapping_AHA_13', 'Mapping_AHA_14', 'Mapping_AHA_15', 'Mapping_AHA_16',
                    'Mapping_Global']
    columns_list = [user_input + '_' + s for s in columns_list]

    df = pd.DataFrame(table, index=processed_list,
                      columns=columns_list
                      )
    df.to_csv(filename)