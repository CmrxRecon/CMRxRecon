%function [mask] = vdPoisMex(sx,sy,fovx,fovy,accelx,accely,calib,ellipse, pp)
%
% function computes a variable density poisson-disc sampling mask
%
% Inputs:
% 	  sx, sy, - size of the image
%	 fovx, fovy - FOV of the actual image in cm
%	 accelx, accely - acceleration in x and y dimensions. 
%	 calib -  number of autocalibration lines
%        ellipse - flag to cut corners. 
%	 pp      - polynomial order of variable density (0 = uniform)
%
%
% Outputs:
%	mask - a binary mask. 
%
%
%   Original function written by Marcus Alley based on a Modification of a python script from 
%   http://devmag.org.za/2009/05/03/poisson-disk-sampling/ . The Mex interface was written by 
%   Michael Lustig 
%
% (c) Michael Lustig 2013


