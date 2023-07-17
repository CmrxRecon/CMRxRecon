# demo of image evaluation

## Package Structure
* `Main_Score`: The main code for scoring (during validation phase, we evaluation NMSE, PSNR and SSIM for both cine and mapping images for simplicity)
* `loadFun`: tools for reading and saving .mat data
* `test_cine`: Test code for cine
* `test_mapping`: Test code for mapping
* `Evaluation`: Metrics definition for reference

## Dependent library 
Package            Version
------------------ ---------
certifi            2023.5.7
cffi               1.15.1
charset-normalizer 3.1.0
cryptography       41.0.1
Deprecated         1.2.14
h5py               3.8.0
idna               3.4
imageio            2.31.1
importlib-metadata 4.13.0
jeepney            0.8.0
keyring            23.4.1
keyrings.alt       3.1
lazy-loader        0.2
networkx           3.1
nibabel            5.1.0
numpy              1.24.3
packaging          23.1
pandas             2.0.2
Pillow             9.5.0
pip                21.0.1
pycparser          2.21
python-dateutil    2.8.2
pytz               2023.3
PyWavelets         1.4.1
rarfile            4.0
requests           2.31.0
scikit-image       0.21.0
scipy              1.10.1
SecretStorage      3.3.3
setuptools         53.0.0
six                1.16.0
synapseclient      2.7.2
tifffile           2023.4.12
tzdata             2023.3
urllib3            1.26.16
wheel              0.36.2
wrapt              1.15.0
zipp               3.15.0
