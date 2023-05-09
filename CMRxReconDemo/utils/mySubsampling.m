function mask = mySubsampling(sx,sy,Nc,ncalib,R)
% Create a sampling mask to simulate xR undersampling with autocalibration lines

% Created by Chengyan Wang
% 06/06/2019
% ------------------------------------------------------------------------------

mask = zpad(ones(sx,ncalib),[sx,sy]);
mask = repmat(mask,[1,1,Nc]);
mask(:,1:R:end,:) = 1;

return