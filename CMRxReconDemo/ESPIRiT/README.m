

This is a collection of Matlab functions and demos to reproduce
some of the results that are described in the papers:

M. Lustig and JM Pauly "SPIRiT: iTerative Self-consistent Parallel Imaging Reconstruction
from Arbitrary k-space", Magnetic Resonance in Medicine, 2010;64(2):457-71

T. Zhang, JM Pauly, SS Vasanawala and M. Lustig "Coil compression for accelerated imaging with Cartesian sampling"
Magn Reson Med, 2013;69(2):571-82

D. Bahri, M. Uecker, M. Lustig, "ESPIRiT-Based Coil Compression for Cartesian Sampling" ISMRM 2013 pp:2657 

M. Uecker, P. Lai, MJ Murphy, P. Virtue, M Elad, JM Pauly, SS Vasanawala and M Lustig, "ESPIRiT- an
eigenvalue approach to autocalibrating parallel MRI: Where SENSE meets GRAPPA", Magn Reson Med, 2013

P. Shin et. al, "Calibrationless Parallel Imaging Reconstruction Based on Structured Low-Rank Matrix Completion" 
2013, submitted to MRM. 

It includes the code previously released in the SPIRiT package and also the GCC package.
Some of the demos revised and those marked by ** USE PUBLISH ** are recommended to run using the Matlab
publish tool, which produces beautiful documents. 


Please contact me at mlustig@eecs.berkeley.edu. You are encouraged to modify/distribute this code. However,
please acknowledge this code and cite the papers appropriately.
This code also includes (with permission) code written by David Donoho (Wavelet Transform)
and Jeffery Fessler (Non-Uniform Fourier Transform)

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


Demos:

SPIRiT:
	demo_spirit_cg.m    : Demonstrates the CG implementation of Cartesian SPIRiT

	demo_l1_spirit_pocs : Demonstrate the POCS implementation of Cartesian SPIRiT
                       with non-linear wavelet thresholding (Compressed Sensing)

	demo_nuSPIRiT       : Demonstrates image-based non-Cartesian SPIRiT

Geometric Decomposition Coil Compression:
	demo_GCC.m	    : Demonstrates geometric decomposition coil compression  ** USE PUBLISH **
	
	demo_ECC.m	    : Demonstrates ESPIRiT based coil compression  ** USE PUBLISH **

	demo_CC_speedup.m   : Demonstrated speedups when using GCC.  ** USE PUBLISH **

ESPIRiT:
	demo_ESPIRiT_maps.m : Demonstrates how to calculate ESPIRiT maps ** USE PUBLISH **

	demo_ESPIRiT_recon.m: Demonstrates ESPIRiT reconstruction with multiple sets of maps ** USE PUBLISH **

	demo_nuESPIRiT.m    : Demonstrates non-Cartesian ESPIRiT

	demo_ESPIRiT_L1_recon.m : Demonstrates L1-Wavelet compressed sensing ESPIRiT ** USE PUBLISH **

	demo_ESPIRiT_parameters.m : Demonstrates how to empirically estimate the ESPIRiT singular value thresholding. ** Publish **

SAKE:
	demo_SAKE.m 		: Demonstrates autocalibration with no explicit autocalibration lines ** Use Publish **


Setup:
To compile the mex files for your architecture execute the make.m script
before starting. 
 
run setpath.m to add all the paths. 



For Any questions, comments and contributions, please contact
Miki Lustig (mlustig@eecs.berkeley.edu)

(c) Michael Lustig 2010, 2013




                      
