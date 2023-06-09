%% This is a demo to generate validation results into the submission folder (this step is required only during validation phase!!!)
% MICCAI "CMRxRecon" challenge 2023 
% 2023.05.06 @ fudan university
% Email: wangcy@fudan.edu.cn

% to reduce the computing burden and space, we only evaluate the central 2 slices
% For cine: use the first 3 time frames for ranking!
% For mapping: we need all weighting for ranking!
% crop the middle 1/6 of the original image for ranking
clc
clear

%% add path
% put your data directory here
basePath = '/Users/apple/Seafile/TempData/Cardiac/RawData/Submission_GRAPPA_Task1/'; %'Submission/'
mainSavePath = '/Users/apple/Seafile/TempData/Cardiac/RawData/Submission/'; %'Submission/'
modality = 'Mapping'; % options: 'Cine' for task1, 'Mapping' for task2

%% do not make changes
AFtype = {'AccFactor04','AccFactor08','AccFactor10'};
setName = 'ValidationSet/'; % options: 'ValidationSet/', 'TestSet/'
if strcmp(modality,'Cine')
    ModalityName{1} = 'cine_lax';
    ModalityName{2} = 'cine_sax';
else
    ModalityName{1} = 'T1map';
    ModalityName{2} = 'T2map';
end    
%% Generate folder for submission
coilInfo = 'MultiCoil/';  % options: 'MultiCoil','SingleCoil'
for ind0 = 1:3
    mainDataPath = strcat(basePath,coilInfo,modality,'/',setName,AFtype{ind0});
    FileList = dir(mainDataPath);
    NumFile = length(FileList);
    k = 0;
    % running all patients
    for ind1 = 1:NumFile
        if isequal(FileList(ind1).name(1),'.')
            k = k+1;
            continue;
        end
        disp(['Progress start for subject ',num2str(ind1-k)]);
        file_name = FileList(ind1).name;
        % modality1
        dataPath = strcat(mainDataPath,'/',file_name,'/',ModalityName{1},'.mat');
        if exist(dataPath,'file')
            dataRecon1 = load(dataPath); % load recon data
            img = dataRecon1.img4ranking; % put your variable name here
            % to reduce the computing burden and space, we only evaluate the central 2 slices
            % For cine: use the first 3 time frames for ranking!
            % For mapping: we need all weighting for ranking!
            img4ranking = run4Ranking(img,ModalityName{1});
            savePath = strcat(mainSavePath,coilInfo,modality,'/',setName,AFtype{ind0});
            % mkdir for saving
            if exist(strcat(savePath,'/',file_name), 'dir') ~= 7
                mkdir(strcat(savePath,'/',file_name));
            end
            save(strcat(savePath,'/',file_name,'/',ModalityName{1},'.mat'),'img4ranking');
        end
        % modality2
        dataPath = strcat(mainDataPath,'/',file_name,'/',ModalityName{2},'.mat');
        if exist(dataPath,'file')
            dataRecon2 = load(dataPath); % load recon data
            img = dataRecon2.img4ranking; % put your variable name here
            % to reduce the computing burden and space, we only evaluate the central 2 slices
            % For cine: use the first 3 time frames for ranking!
            % For mapping: we need all weighting for ranking!
            img4ranking = run4Ranking(img,ModalityName{2});
            savePath = strcat(mainSavePath,coilInfo,modality,'/',setName,AFtype{ind0});
            % mkdir for saving
            if exist(strcat(savePath,'/',file_name), 'dir') ~= 7
                mkdir(strcat(savePath,'/',file_name));
            end
            save(strcat(savePath,'/',file_name,'/',ModalityName{2},'.mat'),'img4ranking');
        end
        disp(strcat(char(AFtype(ind0))," multi coil data generation successful!"));
    end
end
%% single coil
coilInfo = 'SingleCoil/';  % options: 'MultiCoil','SingleCoil'
for ind0 = 1:3
    mainDataPath = strcat(basePath,coilInfo,modality,'/',setName,AFtype{ind0});
    FileList = dir(mainDataPath);
    NumFile = length(FileList);
    k = 0;
    % running all patients
    for ind1 = 1:NumFile
        if isequal(FileList(ind1).name(1),'.')
            k = k+1;
            continue;
        end
        disp(['Progress start for subject ',num2str(ind1-k)]);
        file_name = FileList(ind1).name;
        % modality1
        dataPath = strcat(mainDataPath,'/',file_name,'/',ModalityName{1},'.mat');
        if exist(dataPath,'file')
            dataRecon1 = load(dataPath); % load recon data
            img = dataRecon1.img4ranking; % put your variable name here
            % to reduce the computing burden and space, we only evaluate the central 2 slices
            % For cine: use the first 3 time frames for ranking!
            % For mapping: we need all weighting for ranking!
            img4ranking = run4Ranking(img,ModalityName{1});
            savePath = strcat(mainSavePath,coilInfo,modality,'/',setName,AFtype{ind0});
            % mkdir for saving
            if exist(strcat(savePath,'/',file_name), 'dir') ~= 7
                mkdir(strcat(savePath,'/',file_name));
            end
            save(strcat(savePath,'/',file_name,'/',ModalityName{1},'.mat'),'img4ranking');
        end
        % modality2
        dataPath = strcat(mainDataPath,'/',file_name,'/',ModalityName{2},'.mat');
        if exist(dataPath,'file')
            dataRecon2 = load(dataPath); % load recon data
            img = dataRecon2.img4ranking; % put your variable name here
            % to reduce the computing burden and space, we only evaluate the central 2 slices
            % For cine: use the first 3 time frames for ranking!
            % For mapping: we need all weighting for ranking!
            img4ranking = run4Ranking(img,ModalityName{2});
            savePath = strcat(mainSavePath,coilInfo,modality,'/',setName,AFtype{ind0});
            % mkdir for saving
            if exist(strcat(savePath,'/',file_name), 'dir') ~= 7
                mkdir(strcat(savePath,'/',file_name));
            end
            save(strcat(savePath,'/',file_name,'/',ModalityName{2},'.mat'),'img4ranking');
        end
        disp(strcat(char(AFtype(ind0))," single coil data generation successful!"));
    end
end