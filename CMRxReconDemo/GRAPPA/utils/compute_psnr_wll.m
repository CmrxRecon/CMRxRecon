function psnr = compute_psnr(GndImg, RecImg)
temp = GndImg - RecImg;
[enum, pnum]= size(GndImg);
psnr = 20*log10(sqrt(enum*pnum)*max(GndImg(:))/sqrt((temp(:)'*temp(:))));