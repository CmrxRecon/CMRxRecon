# CMRxRecon Model Pool<br> <span style="float: right"><sub><sup> 2023 MICCAI STACOM Workshop, Updated: 12/01/2024 </sup></sub></span> 

## About
This folder serves as a compilation of reconstruction methods contributed by various teams. 
It contains a comprehensive collection of models developed independently by different participating teams. The codes are named by the team name. For updated version, please refer to the repositories links attached. 


# Teams
1. **hellopipu
    - 📄 [Cite] Fill the K-Space and Refine the Image:Prompting for Dynamic and Multi-Contrast MRI Reconstruction, *Bingyu Xin, Meng Ye, Leon Axel, Dimitris N. Metaxas*
    ```bibtex
    @article{xin2023fill,
    title={Fill the K-Space and Refine the Image: Prompting for Dynamic and Multi-Contrast MRI Reconstruction},
    author={Xin, Bingyu and Ye, Meng and Axel, Leon and Metaxas, Dimitris N},
    journal={arXiv preprint arXiv:2309.13839},
    year={2023}
    }
    ```
    - 💻 [GitHub] https://github.com/hellopipu/PromptMR


2. **Direct
    - 📄 [Cite] Deep Cardiac MRI Reconstruction with ADMM, *George Yiasemis, Nikita Moriakov, Jan-Jakob Sonke, Jonas Teuwen*
    ```bibtex
    @article{Yiasemis2022, 
    doi = {10.21105/joss.04278}, 
    url = {https://doi.org/10.21105/joss.04278}, 
    year = {2022}, publisher = {The Open Journal}, 
    volume = {7}, 
    number = {73}, 
    pages = {4278}, 
    author = {George Yiasemis and Nikita Moriakov and Dimitrios Karkalousos and Matthan Caan and Jonas Teuwen}, 
    title = {DIRECT: Deep Image REConstruction Toolkit}, 
    journal = {Journal of Open Source Software} }
    ```
    - 💻 [GitHub] https://github.com/NKI-AI/direct


3. **clair
    - 📄 [Cite] k-t CLAIR: Self-Consistency Guided Multi-Prior Learning for Dynamic Parallel MR Image Reconstruction, *Liping Zhang, Weitian Chen*
    - 💻 [GitHub] https://github.com/lpzhang/ktCLAIR
    ```bibtex
    @article{zhang2023k,
    title={$ k $-$ t $ CLAIR: Self-Consistency Guided Multi-Prior Learning for Dynamic Parallel MR Image Reconstruction},
    author={Zhang, Liping and Chen, Weitian},
    journal={arXiv preprint arXiv:2310.11050},
    year={2023}
    }
    ```


4. **jabbers
    - 📄 [Cite] NoSENSE: Learned unrolled cardiac MRI reconstruction without explicit sensitivity maps, *Felix Frederik Zimmermann; Andreas Kofler*
    - 💻 [GitHub] https://github.com/fzimmermann89/CMRxRecon #Not applicable
    ```bibtex
    @article{zimmermann2023nosense,
    title={NoSENSE: Learned unrolled cardiac MRI reconstruction without explicit sensitivity maps},
    author={Zimmermann, Felix Frederik and Kofler, Andreas},
    journal={arXiv preprint arXiv:2309.15608},
    year={2023}
    }
    ```


5. **SkolCIG
    - 📄 [Cite] Learnable Objective Image Function for Accelerated MRI Reconstruction, *Artem Razumov and Dmitry V. Dylov*
    - 💻 [GitHub] https://github.com/Airplaneless/cmrx


6. **metaffine
    - 📄 [Cite] Accelerating Cardiac MRI via Deblurring without Sensitivity Estimation, *Jin He, Weizhou Liu, Yun Tian, Shifeng Zhao*
    - 💻 [GitHub] https://github.com/Hejin9/MRI_Recon_via_Deblurring 


7. **Edipo
    - 📄 [Cite] Cine cardiac MRI reconstruction using a convolutional recurrent network with refinement, *Yuyang Xue, Yuning Du, Gianluca Carloni, Eva Pachetti, Connor Jordan, Sotiorios A. Tsaftaris*
    - 💻 [GitHub] https://github.com/vios-s/CMRxRECON_Challenge_EDIPO
    ```bibtex
    @article{xue2023cine,
    title={Cine cardiac MRI reconstruction using a convolutional recurrent network with refinement},
    author={Xue, Yuyang and Du, Yuning and Carloni, Gianluca and Pachetti, Eva and Jordan, Connor and Tsaftaris, Sotirios A},
    journal={arXiv preprint arXiv:2309.13385},
    year={2023}
    }
    ```


8. **hkforest
    - 📄 [Cite] DiffCMR: Fast Cardiac MRI Reconstruction with Diffusion Probabilistic Models *Tianqi Xiang, Wenjun Yue, Yiqun Lin, Jiewen Yang, Zhenkun Wang, Xiaomeng Li*
    ```bibtex
    @article{xiang2023diffcmr,
    title={DiffCMR: Fast Cardiac MRI Reconstruction with Diffusion Probabilistic Models},
    author={Xiang, Tianqi and Yue, Wenjun and Lin, Yiqun and Yang, Jiewen and Wang, Zhenkun and Li, Xiaomeng},
    journal={arXiv preprint arXiv:2312.04853},
    year={2023}
    }
    ```
    - 💻 [GitHub] https://github.com/xmed-lab/DiffCMR


9. **insightdcu
    - 📄 [Cite] Cardiac MRI reconstruction from undersampled k-space using double-stream IFFT and a denoising GNA-UNET pipeline, *Julia Dietlmeier, Carles Garcia-Cabrera, Anam Hashmi, Kathleen M. Curran, Noel E. O’Connor*
    ```bibtex
    @article{dietlmeier2023cardiac,
    title={Cardiac MRI reconstruction from undersampled k-space using double-stream IFFT and a denoising GNA-UNET pipeline},
    author={Dietlmeier, Julia and Garcia-Cabrera, Carles and Hashmi, Anam and Curran, Kathleen M and O'Connor, Noel E},
    year={2023},
    publisher={Springer}
    }
    ```
    - 💻 [GitHub] https://github.com/juliadietlmeier/CMRxRecon_insightdcu


10. **IADI-IMI
    - 📄 [Cite] CineJENSE: Simultaneous Cine MRI Image, *Ziad Al-Haj Hemidi, Nora Vogt, Lucile Quillien, Christian Weihsbach, Mattias P. Heinrich, Julien Oster*
    - 💻 [GitHub] https://github.com/MDL-UzL/CineJENSE


11. **imperial_cmr
    - 📄 [Cite] T1/T2 relaxation temporal modelling from accelerated acquisitions using a Latent Transformer, *Michael Tänzer, Fanwen Wang, Mengyun Qiao, Wenjia Bai, Daniel Rueckert, Guang Yang, Sonia Nielles-Vallespin*
    ```bibtex
    @article{wang2023t1,
    title={T1/T2 relaxation temporal modelling from accelerated acquisitions using a Latent Transformer},
    author={Wang, Fanwen and Tanzer, Michael and Qiao, Mengyun and Bai, Wenjia and Rueckert, Daniel and Yang, Guang and Nielles-Vallespin, Sonia},
    journal={arXiv preprint arXiv:2309.16853},
    year={2023}
    }
    ```
    - 💻 [GitHub] https://github.com/Michael-Tanzer/cmr-x-recon-imperial-2023 #Not applicable


12. **sunnybrook
    - 📄 [Cite] Accelerated Cardiac Parametric Mapping using Deep Learning-Refined Subspace Models, *Calder Sheagren, Brenden Kadota, Jaykumar Patel, Mark Chiew, and Graham Wright*
    - 💻 [GitHub] https://github.com/WrightGroupSRI/CMRxRecon