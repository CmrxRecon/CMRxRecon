% demo for ESPIRIT SENSE recon
% The kspace dimension is assumed to be like this: 
% kspace: complex images with the dimensions (sx,sy,sc,sz,t/w)
% -sx: matrix size in x-axis
% -sy: matrix size in y-axis
% -sc: coil array number
% -sz: slice number (short axis view); slice group (long axis view)
% -t/w: time frame/weighting

% output: img_sense

%% load data
dataPath = '/Users/apple/Seafile/TempData/Cardiac/RawData/ChallengeData/MultiCoil/Cine/ValidationSet/AccFactor04/P002/cine_lax.mat';
load(dataPath); % load raw kspace data
kspace = kspace_sub04; % please check the "ChallengeDataFormat" folder for name description

%% set parameters
ncalib = 24;
kspace_sub = kspace;
[sx,sy,scc,sz,nPhase] = size(kspace_sub);
kspace_cal = zeros(sx,ncalib,scc,sz,nPhase);
isDisplay = 0;
nIterCG = 12; 

%% generate calibration data
for ind2 = 1:nPhase
    kspace_calib = crop(kspace_sub(:,:,:,:,1),sx,ncalib,scc,sz);
    kspace_cal(:,:,:,:,ind2) = kspace_calib;
end

%% SENSE recon
img_sense = zeros(sx,sy,sz,nPhase);
kspace_sense = zeros(sx,sy,scc,sz,nPhase);
% perform sense recon
for ind1 = 1:sz
    for ind2 = 1:nPhase
        % ESPIRiT CG reconstruction with 1 map (SNS is the sensitivity map you need!)
        SNS = myESP_SENSEmap(double(kspace_sub(:,:,:,ind1,ind2)),kspace_cal(:,:,:,ind1,ind2),isDisplay);
        [kspace_sense(:,:,:,ind1,ind2), img_sense(:,:,ind1,ind2)] = cgESPIRiT(double(kspace_sub(:,:,:,ind1,ind2)), SNS, nIterCG,0.01 ,double(kspace_sub(:,:,:,ind1,ind2))*0);
    end
    disp(strcat(num2str(ind1),'/',num2str(sz)," completed!"));
end
if isDisplay == 1
    figure,imshow(abs(img_sense(:,:,1,1)),[0,0.001]); % reconstructed image
end
