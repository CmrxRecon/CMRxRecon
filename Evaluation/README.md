# demo of image evaluation

## Package Structure
* `Main_Score`: The main code for scoring (during validation phase, we evaluation NMSE, PSNR and SSIM for both cine and mapping images for simplicity)
* `loadFun`: tools for reading and saving .mat data
* `test_cine`: Test code for cine
* `test_mapping`: Test code for mapping
* `Evaluation`: Metrics definition for reference