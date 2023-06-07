function runRecon(basePath,mainSavePath,coilInfo,setName,filetype,AFtype,AFname,type,reconType,imgShow)

%% set name
if strcmp(filetype,'cine_lax') || strcmp(filetype,'cine_sax')
    modalityName = 'Cine/';
else
    modalityName = 'Mapping/';    
end

%% run for different Acc factors
for ind0 = 1:3
    mainDataPath = strcat(basePath,coilInfo,modalityName,setName,char(AFtype(ind0)));
    savePath = strcat(mainSavePath,coilInfo,modalityName,setName,char(AFtype(ind0)));
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
        try
            file_name = FileList(ind1).name;
            dataPath = strcat(mainDataPath,'/',file_name,'/',filetype,'.mat');
            load(dataPath); % load raw kspace data
            kspace = eval(char(AFname(ind0)));
            if strcmp(coilInfo,'SingleCoil/')
                [sx,sy,sz,t] = size(kspace);
                kspaceMulti = zeros(sx,sy,1,sz,t);
                kspaceMulti(:,:,1,:,:) = kspace;
                kspace = kspaceMulti;
            end
            % to reduce the computing burden and space, we only evaluate the central 2 slices
            % For cine: use the first 3 time frames for ranking!
            % For mapping: we need all weighting for ranking!
            [sx,sy,~,sz,t] = size(kspace);
            if strcmp(filetype,'cine_lax') || strcmp(filetype,'cine_sax')
                if sz < 3
                    reconImg = ChallengeRecon(kspace(:,:,:,:,1:3), type, reconType, imgShow);
                else
                    reconImg = ChallengeRecon(kspace(:,:,:,round(sz/2)-1:round(sz/2),1:3), type, reconType, imgShow);
                end
                % crop the middle 1/6 of the original image for ranking
                img4ranking = single(crop(abs(reconImg),[round(sx/3),round(sy/2),2,3]));
            else
                reconImg = ChallengeRecon(kspace(:,:,:,round(sz/2)-1:round(sz/2),:), type, reconType, imgShow);
                % crop the middle 1/6 of the original image for ranking
                img4ranking = single(crop(abs(reconImg),[round(sx/3),round(sy/2),2,t]));
            end

            % mkdir for saving
            if exist(strcat(savePath,'/',file_name), 'dir') ~= 7
                mkdir(strcat(savePath,'/',file_name));
            end
            save(strcat(savePath,'/',file_name,'/',filetype,'.mat'),'img4ranking');        
            disp(strcat(char(AFtype(ind0))," reconstructed successfully!"));
        catch
            disp(strcat(char(dataPath)," missing!"));
        end
    end
end
