#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed April 10 00:23:25 2023
Load .mat data using python

@author: c.y.wang
"""

import scipy.io as scio
import numpy as np
from coil_combine import rss_complex

def loadmat(filename):
    # 读取.mat 文件
    mat_file = scio.loadmat(filename)
    # 获取数据集
    dataset = mat_file['img4ranking']
    return dataset


def ifft2c(x):
    # 获取 x 的 shape
    S = np.shape(x)

    # 计算缩放因子
    fctr = S[0] * S[1]

    # 重塑 x
    x = np.reshape(x, (S[0], S[1], np.prod(S[2:])))

    # 初始化结果数组
    res = np.zeros(np.shape(x), dtype=complex)

    # 对每一个通道执行二维傅立叶逆变换
    for n in range(np.shape(x)[2]):
        res[:,:,n] = np.sqrt(fctr) * np.fft.ifftshift(np.fft.ifft2(np.fft.fftshift(x[:,:,n])))

    # 重塑结果数组
    res = np.reshape(res, S)

    return res

def multicoilkdata2img(dataset):
    k_space =np.transpose(dataset,[4,3,2,1,0])
    # 将 k-space 转换为复数数组
    k_space = k_space['real'] + 1j * k_space['imag']
    recon = ifft2c(k_space)
    # 对 k-space 应用快速傅里叶变换
    recon = abs(rss_complex(recon, 2))
    return recon

def kdata2img(dataset):
    k_space = np.transpose(dataset, [3, 2, 1, 0])
    # 将 k-space 转换为复数数组
    k_space = k_space['real'] + 1j * k_space['imag']
    # 对 k-space 应用快速傅里叶变换
    recon = abs(ifft2c(k_space))
    return recon

def loadmat_group(group):
    """
    Load a group in Matlab v7.3 format .mat file using h5py.
    """
    data = {}
    for k, v in group.items():
        if isinstance(v, h5py.Dataset):
            data[k] = v[()]
        elif isinstance(v, h5py.Group):
            data[k] = loadmat_group(v)
    return data