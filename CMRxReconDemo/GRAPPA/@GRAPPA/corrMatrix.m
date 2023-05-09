function [AtA,A] = corrMatrix(kCalib, kSize)

[sx,sy,nCoil] = size(kCalib);

A = [];
y = [];


for n=1:nCoil
	tmp  = im2col(kCalib(:,:,n),kSize,'sliding').';
	A = [A, tmp];
end


AtA = A'*A;

