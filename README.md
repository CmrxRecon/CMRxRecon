# CMRxRecon 2023

## About
Welcome to the Cardiac MRI Reconstruction Challenge 2023 (CMRxRecon2023)！  
The CMRxRecon Challenge is a part of the 26th International Conference on Medical Image Computing and Computer Assisted Intervention, MICCAI 2023, which will be held from October 8th to 12nd 2023 in Vancouver Convention Centre Canada.


[Website](https://cmrxrecon.github.io/) |
[Dataset](https://www.synapse.org/#!Synapse:syn51471091/wiki/) |
[GitHub](https://github.com/CmrxRecon/CMRxRecon/) |
[Publications](#Publication-references)

## Motivation
This challenge aims to establish a platform for fast CMR image reconstruction and provide a benchmark dataset that enables the broad research community to promote advances in this area of research.

## Background
Cardiac magnetic resonance imaging (CMR) has become an important imaging modality for diagnosing cardiac disease due to its superior soft tissue contrast and non-invasiveness. However, an inherent drawback of MRI is that the imaging speed is particularly slow, which will cause discomfort to patients and intr​oduce motion artifacts into images. CMR image reconstruction from highly under-sampled k-space (raw data) has become a hot topic in recent years. 
So far, a large number of AI-based image reconstruction algorithms have shown the potential to improve imaging performance through highly under-sampling data. However, the field of CMR reconstruction still lacks public, standardized, and high-quality datasets. To date, NYU Langone Health has released 'fastMRI' dataset, containing multi-channel knee and brain MRI raw data. However, these images are inadequate for 3D+1D (time domain) applications in cardiac imaging. The goal of establishing the 'CMRxRecon' dataset is to provide a platform that enables the broad research community to participate in this important work.  

This repository contains Matlab code for data loaders, subsampling functions, evaluation metrics, and reference implementations of simple baseline methods. It also contains implementations for methods in some of the publications of the CMRxRecon project.

## Challenge tasks
The ‘CMRxRecon’ challenge include two tasks: 
1) Cine reconstruction

The aim of task 1 is to reduce the readouts and address the image degradation due to motions caused by voluntary breath-holds or cardiac arrhythmia. The final goal will be real-time cine imaging. 

![Task 2](https://github.com/CmrxRecon/CMRxRecon/blob/main/Cine.jpg)
2) T1/T2 mapping

The aim of task 2 is to improve the T1 and T2 mapping estimation accuracy by reducing the readouts and address the image degradation due to motions and under-sampled reconstructions.

![Task 1](https://github.com/CmrxRecon/CMRxRecon/blob/main/Mapping.jpg)

## Documentation

### The CMRxRecon Dataset
A total of 300 healthy volunteers from a single center were included in this study. 
The released dataset include 120 training data, 60 validation data and 120 test data.
Training data include fully sampled k-space data, auto-calibration lines (ACS, 24 lines) and reconstructed images in .m format will be provided.
Validation data include under-sampled k-space data with acceleration factors of 4, 8 and 10, sampling mask, and auto-calibration lines (ACS, 24 lines) will be provided. We will withhold the ground truth images of the validation set.
Test data include under-sampled k-space data with acceleration factors of 4, 8 and 10, sampling mask, auto-calibration lines (ACS, 24 lines) and reconstructed images. The test data will not be available to the participants.

![Image](https://github.com/CmrxRecon/CMRxRecon/blob/main/Image.jpg)

## Package Structure
* `CMRxReconDemo`: contains parallel imaging reconstruction code
* `ChallengeDataFormat`: Explain the challenge data and the rules for data submission
* `Evaluation`: contains image quality evaluation code for validation and testing (from the FastMRI project: https://github.com/facebookresearch/fastMRI/)
* `Mapping`: contains fitting code for T1 mapping and T2 mapping
* `Download_Dataset_Check`: check whether the dataset is completely and rightly downloaded
* `Submission`: contains the structure for challenge submission

## Contact
The code is provided to support reproducible research. If the code is giving syntax error in your particular configuration or some files are missing then you may open an issue or email us at CMRxRecon@outlook.com

## Publication references
You are free to use and/or refer to the CMRxRecon challenge and datasets in your own research after the embargo period (Dec 2023), provided that you cite the following manuscripts: 

**References of the CMRx Series Dataset**
1. Wang C, Lyu J, Wang S, et al. CMRxRecon: A publicly available k-space dataset and benchmark to advance deep learning for cardiac MRI. Scientific Data, 2024, 11(1): 687. Doi: https://doi.org/10.1038/s41597-024-03525-4 
2. Wang Z, Wang F, Qin C, et al. CMRxRecon2024: A Multimodality, Multiview k-Space Dataset Boosting Universal Machine Learning for Accelerated Cardiac MRI, Radiology: Artificial Intelligence, 2025, 7(2): e240443. Doi: https://doi.org/10.1148/ryai.240443
3. Wang Z, Huang M, Shi Z, et al. Enabling Ultra-Fast Cardiovascular Imaging Across Heterogeneous Clinical Environments with a Generalist Foundation Model and Multimodal Database. arXiv preprint arXiv:2512.21652, 2025. Doi: https://doi.org/10.48550/arXiv.2512.21652 
4. Wang C, Li Y, Lv J, et al. Recommendation for Cardiac Magnetic Resonance Imaging-Based Phenotypic Study: Imaging Part. Phenomics. Doi: 2021, 1(4): 151-170. https://doi.org/10.1007/s43657-021-00018-x 

**CMRx Series Challenge Summary Papers**
1. Lyu J, Qin C, Wang S, et al. The state-of-the-art in cardiac MRI reconstruction: Results of the CMRxRecon challenge in MICCAI 2023. Medical Image Analysis, 2025, 101: 103485. Doi: https://doi.org/10.1016/j.media.2025.103485 
2. Wang K, Qin C, Shi Z, et al. Extreme cardiac MRI analysis under respiratory motion: Results of the CMRxMotion Challenge. Medical Image Analysis, 2025: 103883. Doi: https://doi.org/10.1016/j.media.2025.103883
3. Wang F, Wang Z, Li Y, et al. Towards Modality-and Sampling-Universal Learning Strategies for Accelerating Cardiovascular Imaging: Summary of the CMRxRecon2024 Challenge. IEEE Transactions on Medical Imaging, 2025. Doi: 10.1109/TMI.2025.3641610

**Reference for previously algorithms from the organizers:**
1. Wang C, Li Y, Lv J, et al. Recommendation for Cardiac Magnetic Resonance Imaging-Based Phenotypic Study: Imaging Part. Phenomics. 2021, 1(4): 151-170. Doi: https://doi.org/10.1007/s43657-021-00018-x 
2. Lyu J, Li G, Wang C, et al. Region-focused multi-view transformer-based generative adversarial network for cardiac cine MRI reconstruction. Medical Image Analysis, 2023: 102760. Doi: https://doi.org/10.1016/j.media.2023.102760
3. Lyu J, Tian Y, Cai Q, et al. Adaptive channel-modulated personalized federated learning for magnetic resonance image reconstruction. Computers in Biology and Medicine, 2023, 165: 107330. Doi: https://doi.org/10.1016/j.compbiomed.2023.107330
4. Wang Z, Qian C, Guo D, et al. One-dimensional Deep Low-rank and Sparse Network for Accelerated MRI, IEEE Transactions on Medical Imaging, 42: 79-90, 2023. Doi: https://doi.org/10.1109/TMI.2022.3203312
5. Qin C, Schlemper J, Caballero J, et al. Convolutional recurrent neural networks for dynamic MR image reconstruction. IEEE transactions on medical imaging, 2018, 38(1): 280-290. Doi: https://doi.org/10.1109/TMI.2018.2863670
6. Lyu J, Wang S, Tian Y, et al. STADNet: Spatial-Temporal Attention-Guided Dual-Path Network for cardiac cine MRI super-resolution. Medical Image Analysis, 2024;94:103142. Doi: https://doi.org/10.1016/j.media.2024.103142
7. Wang Z, Xiao M, Zhou Y, et al. Deep separable spatiotemporal learning for fast dynamic cardiac MRI. IEEE Transactions on Biomedical Engineering, 2025.  Doi: https://doi.org/10.1109/TBME.2025.3574090 
8. Huang J, Yang L, Wang F, et al. Enhancing global sensitivity and uncertainty quantification in medical image reconstruction with Monte Carlo arbitrary-masked mamba. Medical Image Analysis, 2025, 99: 103334. Doi: https://doi.org/10.1016/j.media.2024.103334
9. Wang Z, Yu X, Wang C, et al. One for multiple: Physics-informed synthetic data boosts generalizable deep learning for fast MRI reconstruction. Medical Image Analysis, 2025, 103: 103616. Doi: https://doi.org/10.1016/j.media.2025.103616
10. Lyu J, Wang G, Wang Z, et al. Diffusion-prior based implicit neural representation for arbitrary-scale cardiac cine MRI super-resolution. Information Fusion, 2025: 103510. Doi: https://doi.org/10.1016/j.inffus.2025.103510
