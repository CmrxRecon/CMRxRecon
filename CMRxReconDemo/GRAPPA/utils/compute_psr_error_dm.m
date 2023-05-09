function [p, s, r, error] = compute_psr_error_dm(label, output)

% label = single(divide_mean(label));
% output = single(divide_mean(output));
label = label ./ max(abs(label(:)));
output = output ./ max(abs(output(:)));
s = ssim(label,output);
p = compute_psnr(label,output);
r = compute_rmse(label,output);
error = abs(label - output);



