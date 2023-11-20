import os
# about file decomposing
import gzip 
import tarfile 
import zipfile 
import rarfile 
# about nii files
import numpy as np
import nibabel as nib


'''processing gz file'''
def ungz(filename): 
    gz_file = gzip.GzipFile(filename)
    #  The single file decompression of a .gz file involves removing the '.gz' extension from the filename.
    filename = filename[:-3]
    with open(filename, "wb+") as file: 
        file.write(gz_file.read()) 
        # This gzip function needs to return a value to further complement the untar function.
        return filename

'''processing tar ball'''
def untar(filename): 
    tar = tarfile.open(filename) 
    names = tar.getnames() 
    folder_dir = '/'.join(filename.split('/')[:-1])
    for name in names: 
        tar.extract(name, folder_dir) 
    tar.close() 

'''processing zip file'''
def unzip(filename): 
    zip_file = zipfile.ZipFile(filename) 
    folder_dir = '/'.join(filename.split('/')[:-1])
    for names in zip_file.namelist(): 
        zip_file.extract(names, folder_dir) 
    zip_file.close() 

'''processing rar file'''
def unrar(filename): 
    rar = rarfile.RarFile(filename) 
    folder_dir = '/'.join(filename.split('/')[:-1])
    # if not os.path.isdir(folder_dir): 
    #     os.mkdir(folder_dir) 
    os.chdir(folder_dir) 
    rar.extractall() 
    rar.close() 


'''unzip ziped file'''
def unzipfile(fpth):
    if '.' in fpth: 
        suffix = fpth.split('.')[-1] 
        if suffix == 'gz': 
            new_filename = ungz(fpth) 
            os.remove(fpth) 
            if new_filename.split('.')[-1] == 'tar': 
                untar(new_filename) 
                os.remove(new_filename)   
        elif suffix == 'tar': 
            untar(fpth) 
            os.remove(fpth) 
        elif suffix == 'zip': 
            unzip(fpth) 
            os.remove(fpth) 
        elif suffix == 'rar': 
            unrar(fpth) 
            os.remove(fpth) 
        return True
    else:
        return False


def nib_load(file_name):
    if not os.path.exists(file_name):
        return np.array([-1])
    proxy = nib.load(file_name)
    data = proxy.get_fdata()
    proxy.uncache()
    return data


def nib_load_w_spacing(file_name):
    if not os.path.exists(file_name):
        return np.array([-1])
    proxy = nib.load(file_name)
    data = proxy.get_fdata()
    spacing = proxy.header.get_zooms()
    proxy.uncache()
    return data, spacing


def nib_affine(file_dir):
    proxy = nib.load(file_dir)
    return proxy.affine
