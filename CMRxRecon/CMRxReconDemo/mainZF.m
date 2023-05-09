%% This is a demo to generate GRAPPA recon results into the submission folder
% The folder name should be changed to "Subimission" before submission
% MICCAI "CMRxRecon" challenge 2023 
% 2023.03.06 @ fudan university
% Email: wangcy@fudan.edu.cn

clc
clear

%% add path
addpath(genpath('./GRAPPA'))
addpath(genpath('./ESPIRiT'))
addpath('./utils')

%% set info
coilInfo = 'MultiCoil/';  % singleCoil is not avalaible for PI recon
setName = 'ValidationSet/'; % options: 'ValidationSet/', 'TestSet/'
AFtype = {'AccFactor04','AccFactor08','AccFactor10'};
AFname = {'kspace_sub04','kspace_sub08','kspace_sub10'};
% personal computer
basePath = '/Users/apple/Seafile/TempData/Cardiac/RawData/ChallengeData/';
mainSavePath = '/Users/apple/Seafile/TempData/Cardiac/RawData/Submission_ZF/';
% % put your data directory here
% basePath = '/media/nas/Seafile_Storage/Raw_data/Processed/CardiacImage/';
% mainSavePath = '/media/nas/Seafile_Storage/Raw_data/MICCAIChallenge2023/';

%% parameter meaning
% type = 0 means full kspace data
% type = 1 means subsampled data

% reconType = 0: perform zero-filling recon
% reconType = 1: perform GRAPPA recon
% reconType = 2: perform SENSE recon
% reconType = 3: perform both GRAPPA and SENSE recon

% imgShow = 0: ignore image imshow
% imgShow = 1: image imshow

% filetype: 'cine_lax', 'cine_sax', 'T1map', 'T2map'

%% ZF recon
type = 1;
reconType = 0;
imgShow = 1;
% long axis cine
runRecon(basePath,mainSavePath,coilInfo,setName,'cine_lax',AFtype,AFname,type,reconType,imgShow); 
% short axis cine
runRecon(basePath,mainSavePath,coilInfo,setName,'cine_sax',AFtype,AFname,type,reconType,imgShow); 
% T1 mapping
runRecon(basePath,mainSavePath,coilInfo,setName,'T1map',AFtype,AFname,type,reconType,imgShow); 
% T2 mapping
runRecon(basePath,mainSavePath,coilInfo,setName,'T2map',AFtype,AFname,type,reconType,imgShow); 