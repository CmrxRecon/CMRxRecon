function [ output_args ] = sos( input_args )
%SOS Summary of this function goes here
%   Detailed explanation goes here

output_args=sqrt(sum(abs(input_args).^2,3));
end

