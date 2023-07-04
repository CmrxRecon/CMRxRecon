
# This script shows how the demo for the multi-coil recon.
import h5py
import numpy as np
from matplotlib import pyplot as plt

import fastmri
from fastmri.data import transforms as T

# load the file
def readfile2numpy(file_name):
    '''
    read the data from mat and convert to numpy array
    '''
    hf = h5py.File(file_name)
    keys = list(hf.keys())
    assert len(keys) == 1, f"Expected only one key in file, got {len(keys)} instead"
    new_value = hf[keys[0]][()]
    data = new_value["real"] + 1j*new_value["imag"]
    return data


def show_coils(data, slice_nums, cmap=None, vmax = 0.0005):
    '''
    plot the figures along the first dims.
    '''
    fig = plt.figure()
    for i, num in enumerate(slice_nums):
        plt.subplot(1, len(slice_nums), i + 1)
        plt.imshow(data[num], cmap=cmap,vmax=vmax)


# here show the filepath of the multi-coil data
file_name = '/media/NAS_CMR/CMRxRecon/ChallengeData/MultiCoil/Cine/TrainingSet/FullSample1/P001/cine_sax.mat'

# read files from mat to numpy
fullmulti = readfile2numpy(file_name)

# choose one slice
slice_kspace = fullmulti[0,5] 

# Convert from numpy array to pytorch tensor
slice_kspace2 = T.to_tensor(slice_kspace)       
# Apply Inverse Fourier Transform to get the complex image       
slice_image = fastmri.ifft2c(slice_kspace2)     
# Compute absolute value to get a real image      
slice_image_abs = fastmri.complex_abs(slice_image)   


show_coils(slice_image_abs, [0, 3, 6], cmap='gray', vmax = 0.0005)
# combine the coil images to a coil-combined ones.
slice_image_rss = fastmri.rss(slice_image_abs, dim=0)

# plot the final images.
plt.imshow(np.abs(slice_image_rss.numpy()), cmap='gray', vmax = 0.0015)