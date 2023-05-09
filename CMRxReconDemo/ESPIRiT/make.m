cd nufft_files

files = dir('*.c');
for n=1:length(files);
    mex(files(n).name);
end

cd ..
cd @Wavelet/private
Makefile

cd ../../

cd utils
mex vdPoisMex.c

cd ../

