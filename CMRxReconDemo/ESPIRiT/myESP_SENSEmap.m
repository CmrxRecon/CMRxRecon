function SNS = myESP_SENSEmap(DATAc,calib,isDisplay)
% generate sensitivity map according to the central calibration lines

if nargin < 4
    isDisplay = 0;
end

ksize = [6,6]; % ESPIRiT kernel-window-size
eigThresh_k = 0.02; % threshold of eigenvectors in k-space
eigThresh_im = 0.9; % threshold of eigenvectors in image space
[sx,sy,Nc] = size(DATAc);

%% Compute Eigen-Value Maps
% Maps are computed in two steps. 
% compute Calibration matrix, perform 1st SVD and convert singular vectors into k-space kernels

[k,S] = dat2Kernel(calib,ksize);
idx = max(find(S >= S(1)*eigThresh_k));

%% Display the singular vectors and values of the calibration matrix
if isDisplay
    kdisp = reshape(k,[ksize(1)*ksize(2)*Nc,ksize(1)*ksize(2)*Nc]);
    figure, subplot(211), plot([1:ksize(1)*ksize(2)*Nc],S,'LineWidth',2);
    hold on, 
    plot([1:ksize(1)*ksize(2)*Nc],S(1)*eigThresh_k,'r-','LineWidth',2);
    plot([idx,idx],[0,S(1)],'g--','LineWidth',2)
    legend('Singular vector value','threshold')
    title('Singular vectors')
    subplot(212), imagesc(abs(kdisp)), colormap(gray(256));
    xlabel('Singular value #');
    title('Singular vectors')
end

%% crop kernels and compute eigen-value decomposition in image space to get maps
[M,W] = kernelEig(k(:,:,:,1:idx),[sx,sy]);

%% show eigen-values and eigen-vectors. The last set of eigen-vectors corresponding to eigen-values 1 look like sensitivity maps
if isDisplay
    figure, imshow3(abs(W),[],[1,Nc]); 
    title('Eigen Values in Image space');
    colormap((gray(256))); colorbar;

    figure, imshow3(abs(M),[],[Nc,Nc]); 
    title('Magnitude of Eigen Vectors');
    colormap(gray(256)); colorbar;

    figure, imshow3(angle(M),[],[Nc,Nc]); 
    title('Magnitude of Eigen Vectors');
    colormap(jet(256)); colorbar;
end


%% Compute SENSE ESPIRiT Maps 
% crop sensitivity maps according to eigenvalues==1. Note that we have to
% use 2 sets of maps. Here we weight the 2 maps with the eigen-values
maps = M(:,:,:,end-1:end);

% % Weight the eigenvectors with soft-senses eigen-values
% weights = W(:,:,end-1:end) ;
% weights = (weights - eigThresh_im)./(1-eigThresh_im).* (W(:,:,end-1:end) > eigThresh_im);
% weights = -cos(pi*weights)/2 + 1/2;
% nIterCG = 12; 

% ESPIRiT CG reconstruction with 1 map (SNS is the sensitivity map you need!)
% disp('Performing SENSE reconstruction from 1 set of maps')
SNS = ESPIRiT(maps(:,:,:,end));
% tic;[reskSENSE, resSENSE] = cgESPIRiT(DATAc, SNS, nIterCG,0.01 ,DATAc*0);toc

return