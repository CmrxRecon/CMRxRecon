function [kspaceCC,kspace_calibCC]  = Coil_compress(kspace,kspace_calib,coilNum)
%% coil compression using ECC
% kspace: [kx,ky,nc]

calib = permute(kspace_calib,[2,1,3]);
eccmtx = calcECCMtx(calib,2,2);
DATAc = permute(kspace,[2,1,3]);
eccmtx_aligned = alignCCMtx(eccmtx(:,1:coilNum,:));

% compress the kspace data
ECCDATA = CC(DATAc,eccmtx_aligned,2);
kspaceCC = permute(ECCDATA,[2,1,3]);
% compress the calibration data
ECCDATAcal = CC(calib,eccmtx_aligned,2);
kspace_calibCC = permute(ECCDATAcal,[2,1,3]);

return