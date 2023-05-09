# CMRxRecon

## About
Welcome to the Cardiac MRI Reconstruction Challenge (CMRxRecon)！  
The CMRxRecon Challenge is a part of the 26th International Conference on Medical Image Computing and Computer Assisted Intervention, MICCAI 2023, which will be held from October 8th to 12nd 2023 in Vancouver Convention Centre Canada.


[Website](https://cmrxrecon.github.io/) |
[Dataset](https://www.synapse.org/#!Synapse:syn51386469/wiki/) |
[GitHub](https://github.com/CmrxRecon/CMRxRecon/) |
[Publications](#Publication references)

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
![Task 2](https://github.com/CmrxRecon/CMRxRecon/Cine.jpg)
2) T1/T2 mapping
The aim of task 2 is to improve the T1 and T2 mapping estimation accuracy by reducing the readouts and address the image degradation due to motions and under-sampled reconstructions.
![Task 1](https://github.com/CmrxRecon/CMRxRecon/Mapping.jpg)

## Documentation

### The CMRxRecon Dataset
A total of 300 healthy volunteers from a single center were included in this study. 
The released dataset include 120 training data, 60 validation data and 120 test data.
Training data include fully sampled k-space data, auto-calibration lines (ACS, 24 lines) and reconstructed images in .m format will be provided.
Validation data include under-sampled k-space data with acceleration factors of 4, 8 and 10, sampling mask, and auto-calibration lines (ACS, 24 lines) will be provided. We will withhold the ground truth images of the validation set.
Test data include under-sampled k-space data with acceleration factors of 4, 8 and 10, sampling mask, auto-calibration lines (ACS, 24 lines) and reconstructed images. The test data will not be available to the participants.

## Package Structure
* `CMRxReconDemo`: contains parallel imaging reconstruction code
* `ChallengeDataFormat`: Explain the challenge data and the rules for data submission
* `Evaluation`: contains image quality evaluation code for validation and testing (from the FastMRI project: https://github.com/facebookresearch/fastMRI/)
* `Mapping`: contains fitting code for T1 mapping and T2 mapping
* `Submission`: contains the structure for challenge submission

## Contact
The code is provided to support reproducible research. If the code is giving syntax error in your particular configuration or some files are missing then you may open an issue or email us at CMRxRecon@outlook.com

## Publication references
You are free to use and/or refer to the CMRxRecon challenge and datasets in your own research after the embargo period (Dec 2023), provided that you cite the following manuscripts: 
Reference of the imaging acquisition protocol: 
1. Wang C, Li Y, Lv J, Jin J, Hu X, Kuang X, Chen W, Wang H. Recommendation for Cardiac Magnetic Resonance Imaging-Based Phenotypic Study: Imaging Part. Phenomics. 2021, 1(4): 151-170. 
Other reference (optional for citation):
1. Wang C, Jang J, Neisius U, Nezafat M, Fahmy A, Kang J, Rodriguez J, Goddu B, Pierce P, Berg S, Zhang J, Wang XY, Nezafat R. Black blood myocardial T2 mapping. Magnetic resonance in medicine. 2019, 81(1): 153-166. 
2. Lyu J, Li G, Wang C, Qin C, Wang S, Qin J. Region-focused multi-view transformer-based generative adversarial network for cardiac cine MRI reconstruction[J]. Medical Image Analysis, 2023: 102760. https://doi.org/10.1016/j.media.2023.102760
3.  Wang S, Qin C, Wang C, et al. The Extreme Cardiac MRI Analysis Challenge under Respiratory Motion (CMRxMotion). arXiv preprint arXiv:2210.06385, 2022. 
