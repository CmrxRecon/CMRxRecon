% to reduce the computing burden and space, we only evaluate the central 2 slices
% For cine: use the first 3 time frames for ranking!
% For mapping: we need all weighting for ranking!
% crop the middle 1/6 of the original image for ranking

%% this function helps you to convert your data for ranking
% img: complex images reconstructed with the dimensions (sx,sy,sz,t/w) in
% original size
% -sx: matrix size in x-axis
% -sy: matrix size in y-axis
% -sz: slice number (short axis view); slice group (long axis view)
% -t/w: time frame/weighting

% img4ranking: "single" format images with the dimensions (sx/3,sy/2,2,3)
% -sx/3: 1/3 of the matrix size in x-axis
% -sy/2: half of the matrix size in y-axis
% img4ranking is the data we used for ranking!!!

function img4ranking = run4Ranking(img,filetype)

[sx,sy,~,sz,t] = size(img);
if strcmp(filetype,'cine_lax') || strcmp(filetype,'cine_sax')
    reconImg = img(:,:,round(sz/2)-1:round(sz/2),1:3);
    % crop the middle 1/6 of the original image for ranking
    img4ranking = single(crop(abs(reconImg),[round(sx/3),round(sy/2),2,3]));
else
    reconImg = img(:,:,round(sz/2)-1:round(sz/2),:);
    % crop the middle 1/6 of the original image for ranking
    img4ranking = single(crop(abs(reconImg),[round(sx/3),round(sy/2),2,t]));
end
        
return