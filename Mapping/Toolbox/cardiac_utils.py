# Copyright 2019, Wenjia Bai. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import os
import math
import numpy as np
import nibabel as nib
import cv2
import vtk
import pandas as pd
import matplotlib.pyplot as plt
from vtk.util import numpy_support
from scipy import interpolate
import skimage
from image_utils import *


def approximate_contour(contour, factor=4, smooth=0.05, periodic=False):
    """ Approximate a contour.

        contour: input contour
        factor: upsampling factor for the contour
        smooth: smoothing factor for controling the number of spline knots.
                Number of knots will be increased until the smoothing
                condition is satisfied:
                sum((w[i] * (y[i]-spl(x[i])))**2, axis=0) <= s
                which means the larger s is, the fewer knots will be used,
                thus the contour will be smoother but also deviating more
                from the input contour.
        periodic: set to True if this is a closed contour, otherwise False.

        return the upsampled and smoothed contour
    """
    # The input contour
    N = len(contour)
    dt = 1.0 / N
    t = np.arange(N) * dt
    x = contour[:, 0]
    y = contour[:, 1]

    # Pad the contour before approximation to avoid underestimating
    # the values at the end points
    r = int(0.5 * N)
    t_pad = np.concatenate((np.arange(-r, 0) * dt, t, 1 + np.arange(0, r) * dt))
    if periodic:
        x_pad = np.concatenate((x[-r:], x, x[:r]))
        y_pad = np.concatenate((y[-r:], y, y[:r]))
    else:
        x_pad = np.concatenate((np.repeat(x[0], repeats=r), x, np.repeat(x[-1], repeats=r)))
        y_pad = np.concatenate((np.repeat(y[0], repeats=r), y, np.repeat(y[-1], repeats=r)))

    # Fit the contour with splines with a smoothness constraint
    fx = interpolate.UnivariateSpline(t_pad, x_pad, s=smooth * len(t_pad))
    fy = interpolate.UnivariateSpline(t_pad, y_pad, s=smooth * len(t_pad))

    # Evaluate the new contour
    N2 = N * factor
    dt2 = 1.0 / N2
    t2 = np.arange(N2) * dt2
    x2, y2 = fx(t2), fy(t2)
    contour2 = np.stack((x2, y2), axis=1)
    return contour2


def sa_pass_quality_control(seg_sa_name):
    """ Quality control for short-axis image segmentation """
    nim = nib.load(seg_sa_name)
    seg_sa = nim.get_data()
    X, Y, Z = seg_sa.shape[:3]

    # Label class in the segmentation
    label = {'LV': 1, 'Myo': 2, 'RV': 3}

    # Criterion 1: every class exists and the area is above a threshold
    # Count number of pixels in 3D
    for l_name, l in label.items():
        pixel_thres = 10
        if np.sum(seg_sa == l) < pixel_thres:
            print('{0}: The segmentation for class {1} is smaller than {2} pixels. '
                  'It does not pass the quality control.'.format(seg_sa_name, l_name, pixel_thres))
            return False

    # Criterion 2: number of slices with LV segmentations is above a threshold
    # and there is no missing segmentation in between the slices
    z_pos = []
    for z in range(Z):
        seg_z = seg_sa[:, :, z]
        endo = (seg_z == label['LV']).astype(np.uint8)
        myo = (seg_z == label['Myo']).astype(np.uint8)
        pixel_thres = 10
        if (np.sum(endo) < pixel_thres) or (np.sum(myo) < pixel_thres):
            continue
        z_pos += [z]
    n_slice = len(z_pos)
    slice_thres = 6
    if n_slice < slice_thres:
        print('{0}: The segmentation has less than {1} slices. '
              'It does not pass the quality control.'.format(seg_sa_name, slice_thres))
        return False

    if n_slice != (np.max(z_pos) - np.min(z_pos) + 1):
        print('{0}: There is missing segmentation between the slices. '
              'It does not pass the quality control.'.format(seg_sa_name))
        return False

    # Criterion 3: LV and RV exists on the mid-cavity slice
    _, _, cz = [np.mean(x) for x in np.nonzero(seg_sa == label['LV'])]
    z = int(round(cz))
    seg_z = seg_sa[:, :, z]

    endo = (seg_z == label['LV']).astype(np.uint8)
    endo = get_largest_cc(endo).astype(np.uint8)
    myo = (seg_z == label['Myo']).astype(np.uint8)
    myo = remove_small_cc(myo).astype(np.uint8)
    epi = (endo | myo).astype(np.uint8)
    epi = get_largest_cc(epi).astype(np.uint8)
    rv = (seg_z == label['RV']).astype(np.uint8)
    rv = get_largest_cc(rv).astype(np.uint8)
    pixel_thres = 10
    if np.sum(epi) < pixel_thres or np.sum(rv) < pixel_thres:
        print('{0}: Can not find LV epi or RV to determine the AHA '
              'coordinate system.'.format(seg_sa_name))
        return False
    return True


def la_pass_quality_control(seg_la_name):
    """ Quality control for long-axis image segmentation """
    nim = nib.load(seg_la_name)
    seg = nim.get_data()
    X, Y, Z = seg.shape[:3]
    seg_z = seg[:, :, 0]

    # Label class in the segmentation
    label = {'LV': 1, 'Myo': 2, 'RV': 3, 'LA': 4, 'RA': 5}

    for l_name, l in label.items():
        # Criterion 1: every class exists and the area is above a threshold
        pixel_thres = 10
        if np.sum(seg_z == l) < pixel_thres:
            print('{0}: The segmentation for class {1} is smaller than {2} pixels. '
                  'It does not pass the quality control.'.format(seg_la_name, l_name, pixel_thres))
            return False

    # Criterion 2: the area is above a threshold after connected component analysis
    endo = (seg_z == label['LV']).astype(np.uint8)
    endo = get_largest_cc(endo).astype(np.uint8)
    myo = (seg_z == label['Myo']).astype(np.uint8)
    myo = remove_small_cc(myo).astype(np.uint8)
    epi = (endo | myo).astype(np.uint8)
    epi = get_largest_cc(epi).astype(np.uint8)
    pixel_thres = 10
    if np.sum(endo) < pixel_thres or np.sum(myo) < pixel_thres or np.sum(epi) < pixel_thres:
        print('{0}: Can not find LV endo, myo or epi to extract the long-axis '
              'myocardial contour.'.format(seg_la_name))
        return False
    return True


def determine_aha_coordinate_system(seg_sa, affine_sa):
    """ Determine the AHA coordinate system using the mid-cavity slice
        of the short-axis image segmentation.
        """
    # Label class in the segmentation
    label = {'BG': 0, 'LV': 1, 'Myo': 2, 'RV': 3}

    # Find the mid-cavity slice
    _, _, cz = [np.mean(x) for x in np.nonzero(seg_sa == label['LV'])]
    z = int(round(cz))
    seg_z = seg_sa[:, :, z]

    endo = (seg_z == label['LV']).astype(np.uint8)
    endo = get_largest_cc(endo).astype(np.uint8)
    myo = (seg_z == label['Myo']).astype(np.uint8)
    myo = remove_small_cc(myo).astype(np.uint8)
    epi = (endo | myo).astype(np.uint8)
    epi = get_largest_cc(epi).astype(np.uint8)
    rv = (seg_z == label['RV']).astype(np.uint8)
    rv = get_largest_cc(rv).astype(np.uint8)

    # Extract epicardial contour
    contours, _ = cv2.findContours(cv2.inRange(epi, 1, 1), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    epi_contour = contours[0][:, 0, :]

    # Find the septum, which is the intersection between LV and RV
    septum = []
    dilate_iter = 1
    while len(septum) == 0:
        # Dilate the RV till it intersects with LV epicardium.
        # Normally, this is fulfilled after just one iteration.
        rv_dilate = cv2.dilate(rv, np.ones((3, 3), dtype=np.uint8), iterations=dilate_iter)
        dilate_iter += 1
        for y, x in epi_contour:
            if rv_dilate[x, y] == 1:
                septum += [[x, y]]

    # The middle of the septum
    mx, my = septum[int(round(0.5 * len(septum)))]
    point_septum = np.dot(affine_sa, np.array([mx, my, z, 1]))[:3]

    # Find the centre of the LV cavity
    cx, cy = [np.mean(x) for x in np.nonzero(endo)]
    point_cavity = np.dot(affine_sa, np.array([cx, cy, z, 1]))[:3]

    # Determine the AHA coordinate system
    axis = {}
    axis['lv_to_sep'] = point_septum - point_cavity
    axis['lv_to_sep'] /= np.linalg.norm(axis['lv_to_sep'])
    axis['apex_to_base'] = np.copy(affine_sa[:3, 2])
    axis['apex_to_base'] /= np.linalg.norm(axis['apex_to_base'])
    if axis['apex_to_base'][2] < 0:
        axis['apex_to_base'] *= -1
    axis['inf_to_ant'] = np.cross(axis['apex_to_base'], axis['lv_to_sep'])
    return axis


def determine_aha_part(seg_sa, affine_sa, three_slices=False):
    """ Determine the AHA part for each slice. """
    # Label class in the segmentation
    label = {'BG': 0, 'LV': 1, 'Myo': 2, 'RV': 3}

    # Sort the z-axis positions of the slices with both endo and epicardium
    # segmentations
    X, Y, Z = seg_sa.shape[:3]
    z_pos = []
    for z in range(Z):
        seg_z = seg_sa[:, :, z]
        endo = (seg_z == label['LV']).astype(np.uint8)
        myo = (seg_z == label['Myo']).astype(np.uint8)
        pixel_thres = 10
        if (np.sum(endo) < pixel_thres) or (np.sum(myo) < pixel_thres):
            continue
        z_pos += [(z, np.dot(affine_sa, np.array([X / 2.0, Y / 2.0, z, 1]))[2])]
    z_pos = sorted(z_pos, key=lambda x: -x[1])

    # Divide the slices into three parts: basal, mid-cavity and apical
    n_slice = len(z_pos)
    part_z = {}
    if three_slices:
        # Select three slices (basal, mid and apical) for strain analysis, inspired by:
        #
        # [1] Robin J. Taylor, et al. Myocardial strain measurement with
        # feature-tracking cardiovascular magnetic resonance: normal values.
        # European Heart Journal - Cardiovascular Imaging, (2015) 16, 871-881.
        #
        # [2] A. Schuster, et al. Cardiovascular magnetic resonance feature-
        # tracking assessment of myocardial mechanics: Intervendor agreement
        # and considerations regarding reproducibility. Clinical Radiology
        # 70 (2015), 989-998.

        # Use the slice at 25% location from base to apex.
        # Avoid using the first one or two basal slices, as the myocardium
        # will move out of plane at ES due to longitudinal motion, which will
        # be a problem for 2D in-plane motion tracking.
        z = int(round((n_slice - 1) * 0.25))
        part_z[z_pos[z][0]] = 'basal'

        # Use the central slice.
        z = int(round((n_slice - 1) * 0.5))
        part_z[z_pos[z][0]] = 'mid'

        # Use the slice at 75% location from base to apex.
        # In the most apical slices, the myocardium looks blurry and
        # may not be suitable for motion tracking.
        z = int(round((n_slice - 1) * 0.75))
        part_z[z_pos[z][0]] = 'apical'
    else:
        # Use all the slices
        i1 = int(math.ceil(n_slice / 3.0))
        i2 = int(math.ceil(2 * n_slice / 3.0))
        i3 = n_slice

        for i in range(0, i1):
            part_z[z_pos[i][0]] = 'basal'

        for i in range(i1, i2):
            part_z[z_pos[i][0]] = 'mid'

        for i in range(i2, i3):
            part_z[z_pos[i][0]] = 'apical'
    return part_z


def return_aha16_mask(seg_data,lv_centre,aha_axis,part):
    np.where( (tem_func(seg_data,lv_centre,aha_axis)>=-30)
              and
              (tem_func(seg_data,lv_centre,aha_axis)<30),
              1,0
    )

    np.where((tem_func(seg_data, lv_centre, aha_axis) >= -30)
             and
             (tem_func(seg_data, lv_centre, aha_axis) < 30)
             )

def tem_func(seg_data,lv_centre,aha_axis):
    return math.degrees(math.atan2( np.dot(seg_data - lv_centre, aha_axis['lv_to_sep']),
                                    np.dot(seg_data - lv_centre, aha_axis['inf_to_ant'])
                                   )
                        )


def determine_aha_segment_id(point, lv_centre, aha_axis, part):
    """ Determine the AHA segment ID given a point,
        the LV cavity center and the coordinate system.
        """
    d = point - lv_centre
    x = np.dot(d, aha_axis['inf_to_ant'])
    y = np.dot(d, aha_axis['lv_to_sep'])
    deg = math.degrees(math.atan2(y, x))
    seg_id = 0
    if part == 'basal':
        if (deg >= -30) and (deg < 30):
            seg_id = 1
        elif (deg >= 30) and (deg < 90):
            seg_id = 2
        elif (deg >= 90) and (deg < 150):
            seg_id = 3
        elif (deg >= 150) or (deg < -150):
            seg_id = 4
        elif (deg >= -150) and (deg < -90):
            seg_id = 5
        elif (deg >= -90) and (deg < -30):
            seg_id = 6
        else:
            print('Error: wrong degree {0}!'.format(deg))
            exit(0)
    elif part == 'mid':
        if (deg >= -30) and (deg < 30):
            seg_id = 7
        elif (deg >= 30) and (deg < 90):
            seg_id = 8
        elif (deg >= 90) and (deg < 150):
            seg_id = 9
        elif (deg >= 150) or (deg < -150):
            seg_id = 10
        elif (deg >= -150) and (deg < -90):
            seg_id = 11
        elif (deg >= -90) and (deg < -30):
            seg_id = 12
        else:
            print('Error: wrong degree {0}!'.format(deg))
            exit(0)
    elif part == 'apical':
        if (deg >= -45) and (deg < 45):
            seg_id = 13
        elif (deg >= 45) and (deg < 135):
            seg_id = 14
        elif (deg >= 135) or (deg < -135):
            seg_id = 15
        elif (deg >= -135) and (deg < -45):
            seg_id = 16
        else:
            print('Error: wrong degree {0}!'.format(deg))
            exit(0)
    elif part == 'apex':
        seg_id = 17
    else:
        print('Error: unknown part {0}!'.format(part))
        exit(0)
    return seg_id


def evaluate_myo_AHA_mapping(seg_name, map_name, mapping_type, part=None):
    """
    mapping_type: 'T1' or 'T2', str
    aha_mask: aha_id(1-16) for each pixel, and 0 for no myo part
    """
    # Read the segmentation image
    nim = nib.load(seg_name)
    Z = nim.header['dim'][3]
    affine = nim.affine
    seg = nim.get_data()
    # Read the mapping image(t1 or t2)
    nim_map = nib.load(map_name)
    mapping = nim_map.get_data()

    # Label class in the segmentation
    label = {'BG': 0, 'LV': 1, 'Myo': 2, 'RV': 3}

    # Determine the AHA coordinate system using the mid-cavity slice
    aha_axis = determine_aha_coordinate_system(seg, affine)

    # Determine the AHA part of each slice
    part_z = {}
    if not part:
        part_z = determine_aha_part(seg, affine)
    else:
        part_z = {z: part for z in range(Z)}


    aha_mask = np.zeros_like(seg).astype(np.uint8)
    # For each slice
    for z in range(Z):
        # Check whether there is endocardial segmentation and it is not too small,
        # e.g. a single pixel, which either means the structure is missing or
        # causes problem in contour interpolation.
        seg_z = seg[:, :, z]
        endo = (seg_z == label['LV']).astype(np.uint8)
        endo = get_largest_cc(endo).astype(np.uint8)
        myo = (seg_z == label['Myo']).astype(np.uint8)
        myo = remove_small_cc(myo).astype(np.uint8)
        epi = (endo | myo).astype(np.uint8)
        epi = get_largest_cc(epi).astype(np.uint8)
        pixel_thres = 10
        if (np.sum(endo) < pixel_thres) or (np.sum(myo) < pixel_thres):
            continue
        # Calculate the centre of the LV cavity
        # Get the largest component in case we have a bad segmentation
        cx, cy = [np.mean(x) for x in np.nonzero(endo)]
        lv_centre = np.dot(affine, np.array([cx, cy, z, 1]))[:3]

        aha_mask_z = np.zeros_like(seg_z).astype(np.uint8)

        # for each point in myo label of slice z
        x_myo, y_myo = np.where(myo==1)
        # z_myo = np.ones_like(x_myo)*z
        for x,y in zip(x_myo,y_myo):
            p = np.dot(affine, np.array([x, y, z, 1]))[:3]
            seg_id = determine_aha_segment_id(p, lv_centre, aha_axis, part_z[z])
            aha_mask_z[x,y]=seg_id

        aha_mask[:,:,z] = aha_mask_z

    aha17_mapping = np.zeros(17) # 17(1-16,and Global mean)
    for i in range(16):
        aha17_mapping[i]=np.mean(mapping[aha_mask==i+1])

    # print(np.mean(mapping[aha_mask != 0]))
    aha17_mapping[-1] = np.mean(mapping[aha_mask != 0])

    index = [str(x) for x in np.arange(1, 17)] + ['Global'+mapping_type]
    df = pd.DataFrame(aha17_mapping, index=index, columns=['Mapping'])

    return df

def evaluate_wall_thickness(seg_name, output_name_stem, part=None):
    """ Evaluate myocardial wall thickness. """
    # Read the segmentation image
    nim = nib.load(seg_name)
    Z = nim.header['dim'][3]
    affine = nim.affine
    seg = nim.get_data()

    # Label class in the segmentation
    label = {'BG': 0, 'LV': 1, 'Myo': 2, 'RV': 3}

    # Determine the AHA coordinate system using the mid-cavity slice
    aha_axis = determine_aha_coordinate_system(seg, affine)

    # Determine the AHA part of each slice
    part_z = {}
    if not part:
        part_z = determine_aha_part(seg, affine)
    else:
        part_z = {z: part for z in range(Z)}

    # Construct the points set to represent the endocardial contours
    endo_points = vtk.vtkPoints()
    thickness = vtk.vtkDoubleArray()
    thickness.SetName('Thickness')
    points_aha = vtk.vtkIntArray()
    points_aha.SetName('Segment ID')
    point_id = 0
    lines = vtk.vtkCellArray()

    # Save epicardial contour for debug and demonstration purposes
    save_epi_contour = False
    if save_epi_contour:
        epi_points = vtk.vtkPoints()
        points_epi_aha = vtk.vtkIntArray()
        points_epi_aha.SetName('Segment ID')
        point_epi_id = 0
        lines_epi = vtk.vtkCellArray()

    # For each slice
    for z in range(Z):
        # Check whether there is endocardial segmentation and it is not too small,
        # e.g. a single pixel, which either means the structure is missing or
        # causes problem in contour interpolation.
        seg_z = seg[:, :, z]
        endo = (seg_z == label['LV']).astype(np.uint8)
        endo = get_largest_cc(endo).astype(np.uint8)
        myo = (seg_z == label['Myo']).astype(np.uint8)
        myo = remove_small_cc(myo).astype(np.uint8)
        epi = (endo | myo).astype(np.uint8)
        epi = get_largest_cc(epi).astype(np.uint8)
        pixel_thres = 10
        if (np.sum(endo) < pixel_thres) or (np.sum(myo) < pixel_thres):
            continue

        # Calculate the centre of the LV cavity
        # Get the largest component in case we have a bad segmentation
        cx, cy = [np.mean(x) for x in np.nonzero(endo)]
        lv_centre = np.dot(affine, np.array([cx, cy, z, 1]))[:3]

        # Extract endocardial contour
        # Note: cv2 considers an input image as a Y x X array, which is different
        # from nibabel which assumes a X x Y array.
        _, contours, _ = cv2.findContours(cv2.inRange(endo, 1, 1), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        endo_contour = contours[0][:, 0, :]

        # Extract epicardial contour
        _, contours, _ = cv2.findContours(cv2.inRange(epi, 1, 1), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        epi_contour = contours[0][:, 0, :]

        # Smooth the contours
        endo_contour = approximate_contour(endo_contour, periodic=True)
        epi_contour = approximate_contour(epi_contour, periodic=True)

        # A polydata representation of the epicardial contour
        epi_points_z = vtk.vtkPoints()
        for y, x in epi_contour:
            p = np.dot(affine, np.array([x, y, z, 1]))[:3]
            epi_points_z.InsertNextPoint(p)
        epi_poly_z = vtk.vtkPolyData()
        epi_poly_z.SetPoints(epi_points_z)

        # Point locator for the epicardial contour
        locator = vtk.vtkPointLocator()
        locator.SetDataSet(epi_poly_z)
        locator.BuildLocator()

        # For each point on endocardium, find the closest point on epicardium
        N = endo_contour.shape[0]
        for i in range(N):
            y, x = endo_contour[i]

            # The world coordinate of this point
            p = np.dot(affine, np.array([x, y, z, 1]))[:3]
            endo_points.InsertNextPoint(p)

            # The closest epicardial point
            q = np.array(epi_points_z.GetPoint(locator.FindClosestPoint(p)))

            # The distance from endo to epi
            dist_pq = np.linalg.norm(q - p)

            # Add the point data
            thickness.InsertNextTuple1(dist_pq)
            seg_id = determine_aha_segment_id(p, lv_centre, aha_axis, part_z[z])
            points_aha.InsertNextTuple1(seg_id)

            # Record the first point of the current contour
            if i == 0:
                contour_start_id = point_id

            # Add the line
            if i == (N - 1):
                lines.InsertNextCell(2, [point_id, contour_start_id])
            else:
                lines.InsertNextCell(2, [point_id, point_id + 1])

            # Increment the point index
            point_id += 1

        if save_epi_contour:
            # For each point on epicardium
            N = epi_contour.shape[0]
            for i in range(N):
                y, x = epi_contour[i]

                # The world coordinate of this point
                p = np.dot(affine, np.array([x, y, z, 1]))[:3]
                epi_points.InsertNextPoint(p)
                seg_id = determine_aha_segment_id(p, lv_centre, aha_axis, part_z[z])
                points_epi_aha.InsertNextTuple1(seg_id)

                # Record the first point of the current contour
                if i == 0:
                    contour_start_id = point_epi_id

                # Add the line
                if i == (N - 1):
                    lines_epi.InsertNextCell(2, [point_epi_id, contour_start_id])
                else:
                    lines_epi.InsertNextCell(2, [point_epi_id, point_epi_id + 1])

                # Increment the point index
                point_epi_id += 1

    # Save to a vtk file
    endo_poly = vtk.vtkPolyData()
    endo_poly.SetPoints(endo_points)
    endo_poly.GetPointData().AddArray(thickness)
    endo_poly.GetPointData().AddArray(points_aha)
    endo_poly.SetLines(lines)

    writer = vtk.vtkPolyDataWriter()
    output_name = '{0}.vtk'.format(output_name_stem)
    writer.SetFileName(output_name)
    writer.SetInputData(endo_poly)
    writer.Write()

    if save_epi_contour:
        epi_poly = vtk.vtkPolyData()
        epi_poly.SetPoints(epi_points)
        epi_poly.GetPointData().AddArray(points_epi_aha)
        epi_poly.SetLines(lines_epi)
        writer = vtk.vtkPolyDataWriter()
        output_name = '{0}_epi.vtk'.format(output_name_stem)
        writer.SetFileName(output_name)
        writer.SetInputData(epi_poly)
        writer.Write()

    # Evaluate the wall thickness per AHA segment and save to a csv file
    table_thickness = np.zeros(17)
    table_thickness_max = np.zeros(17)
    np_thickness = numpy_support.vtk_to_numpy(thickness).astype(np.float32)
    np_points_aha = numpy_support.vtk_to_numpy(points_aha).astype(np.int8)

    for i in range(16):
        table_thickness[i] = np.mean(np_thickness[np_points_aha == (i + 1)])
        table_thickness_max[i] = np.max(np_thickness[np_points_aha == (i + 1)])
    table_thickness[-1] = np.mean(np_thickness)
    table_thickness_max[-1] = np.max(np_thickness)

    index = [str(x) for x in np.arange(1, 17)] + ['Global']
    df = pd.DataFrame(table_thickness, index=index, columns=['Thickness'])
    df.to_csv('{0}.csv'.format(output_name_stem))

    df = pd.DataFrame(table_thickness_max, index=index, columns=['Thickness_Max'])
    df.to_csv('{0}_max.csv'.format(output_name_stem))


def extract_myocardial_contour(seg_name, contour_name_stem, part=None, three_slices=False):
    """ Extract the myocardial contours, including both endo and epicardial contours.
        Determine the AHA segment ID for all the contour points.

        By default, part is None. This function will automatically determine the part
        for each slice (basal, mid or apical).
        If part is given, this function will use the given part for the image slice.
        """
    # Read the segmentation image
    nim = nib.load(seg_name)
    X, Y, Z = nim.header['dim'][1:4]
    affine = nim.affine
    seg = nim.get_data()

    # Label class in the segmentation
    label = {'BG': 0, 'LV': 1, 'Myo': 2, 'RV': 3}

    # Determine the AHA coordinate system using the mid-cavity slice
    aha_axis = determine_aha_coordinate_system(seg, affine)

    # Determine the AHA part of each slice
    part_z = {}
    if not part:
        part_z = determine_aha_part(seg, affine, three_slices=three_slices)
    else:
        part_z = {z: part for z in range(Z)}

    # For each slice
    for z in range(Z):
        # Check whether there is the endocardial segmentation
        seg_z = seg[:, :, z]
        endo = (seg_z == label['LV']).astype(np.uint8)
        endo = get_largest_cc(endo).astype(np.uint8)
        myo = (seg_z == label['Myo']).astype(np.uint8)
        myo = remove_small_cc(myo).astype(np.uint8)
        epi = (endo | myo).astype(np.uint8)
        epi = get_largest_cc(epi).astype(np.uint8)
        pixel_thres = 10
        if (np.sum(endo) < pixel_thres) or (np.sum(myo) < pixel_thres):
            continue

        # Check whether this slice is going to be analysed
        if z not in part_z.keys():
            continue

        # Construct the points set and data arrays to represent both endo and epicardial contours
        points = vtk.vtkPoints()
        points_radial = vtk.vtkFloatArray()
        points_radial.SetName('Direction_Radial')
        points_radial.SetNumberOfComponents(3)
        points_label = vtk.vtkIntArray()
        points_label.SetName('Label')
        points_aha = vtk.vtkIntArray()
        points_aha.SetName('Segment ID')
        point_id = 0

        lines = vtk.vtkCellArray()
        lines_aha = vtk.vtkIntArray()
        lines_aha.SetName('Segment ID')
        lines_dir = vtk.vtkIntArray()
        lines_dir.SetName('Direction ID')

        # Calculate the centre of the LV cavity
        # Get the largest component in case we have a bad segmentation
        cx, cy = [np.mean(x) for x in np.nonzero(endo)]
        lv_centre = np.dot(affine, np.array([cx, cy, z, 1]))[:3]

        # Extract epicardial contour
        _, contours, _ = cv2.findContours(cv2.inRange(epi, 1, 1), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        epi_contour = contours[0][:, 0, :]
        epi_contour = approximate_contour(epi_contour, periodic=True)

        N = epi_contour.shape[0]
        for i in range(N):
            y, x = epi_contour[i]

            # The world coordinate of this point
            p = np.dot(affine, np.array([x, y, z, 1]))[:3]
            points.InsertNextPoint(p[0], p[1], p[2])

            # The radial direction from the cavity centre to this point
            d_rad = p - lv_centre
            d_rad = d_rad / np.linalg.norm(d_rad)
            points_radial.InsertNextTuple3(d_rad[0], d_rad[1], d_rad[2])

            # Record the type of the point (1 = endo, 2 = epi)
            points_label.InsertNextTuple1(2)

            # Record the AHA segment ID
            seg_id = determine_aha_segment_id(p, lv_centre, aha_axis, part_z[z])
            points_aha.InsertNextTuple1(seg_id)

            # Record the first point of the current contour
            if i == 0:
                contour_start_id = point_id

            # Add the circumferential line
            if i == (N - 1):
                lines.InsertNextCell(2, [point_id, contour_start_id])
            else:
                lines.InsertNextCell(2, [point_id, point_id + 1])

            lines_aha.InsertNextTuple1(seg_id)

            # Line direction (1 = radial, 2 = circumferential, 3 = longitudinal)
            lines_dir.InsertNextTuple1(2)

            # Increment the point index
            point_id += 1

        # Point locator
        epi_points = vtk.vtkPoints()
        epi_points.DeepCopy(points)
        epi_poly = vtk.vtkPolyData()
        epi_poly.SetPoints(epi_points)
        locator = vtk.vtkPointLocator()
        locator.SetDataSet(epi_poly)
        locator.BuildLocator()

        # Extract endocardial contour
        # Note: cv2 considers an input image as a Y x X array, which is different
        # from nibabel which assumes a X x Y array.
        _, contours, _ = cv2.findContours(cv2.inRange(endo, 1, 1), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        endo_contour = contours[0][:, 0, :]
        endo_contour = approximate_contour(endo_contour, periodic=True)

        N = endo_contour.shape[0]
        for i in range(N):
            y, x = endo_contour[i]

            # The world coordinate of this point
            p = np.dot(affine, np.array([x, y, z, 1]))[:3]
            points.InsertNextPoint(p[0], p[1], p[2])

            # The radial direction from the cavity centre to this point
            d_rad = p - lv_centre
            d_rad = d_rad / np.linalg.norm(d_rad)
            points_radial.InsertNextTuple3(d_rad[0], d_rad[1], d_rad[2])

            # Record the type of the point (1 = endo, 2 = epi)
            points_label.InsertNextTuple1(1)

            # Record the AHA segment ID
            seg_id = determine_aha_segment_id(p, lv_centre, aha_axis, part_z[z])
            points_aha.InsertNextTuple1(seg_id)

            # Record the first point of the current contour
            if i == 0:
                contour_start_id = point_id

            # Add the circumferential line
            if i == (N - 1):
                lines.InsertNextCell(2, [point_id, contour_start_id])
            else:
                lines.InsertNextCell(2, [point_id, point_id + 1])

            lines_aha.InsertNextTuple1(seg_id)

            # Line direction (1 = radial, 2 = circumferential, 3 = longitudinal)
            lines_dir.InsertNextTuple1(2)

            # Add the radial line for every few points
            n_radial = 36
            M = int(round(N / float(n_radial)))
            if i % M == 0:
                # The closest epicardial points
                ids = vtk.vtkIdList()
                n_ids = 10
                locator.FindClosestNPoints(n_ids, p, ids)

                # The point that aligns with the radial direction
                val = []
                for j in range(n_ids):
                    q = epi_points.GetPoint(ids.GetId(j))
                    d = (q - lv_centre) / np.linalg.norm(q - lv_centre)
                    val += [np.dot(d, d_rad)]
                val = np.array(val)
                epi_point_id = ids.GetId(np.argmax(val))

                # Add the radial line
                lines.InsertNextCell(2, [point_id, epi_point_id])
                lines_aha.InsertNextTuple1(seg_id)

                # Line direction (1 = radial, 2 = circumferential, 3 = longitudinal)
                lines_dir.InsertNextTuple1(1)

            # Increment the point index
            point_id += 1

        # Save the contour for each slice
        poly = vtk.vtkPolyData()
        poly.SetPoints(points)
        poly.GetPointData().AddArray(points_label)
        poly.GetPointData().AddArray(points_aha)
        poly.GetPointData().AddArray(points_radial)
        poly.SetLines(lines)
        poly.GetCellData().AddArray(lines_aha)
        poly.GetCellData().AddArray(lines_dir)

        writer = vtk.vtkPolyDataWriter()
        contour_name = '{0}{1:02d}.vtk'.format(contour_name_stem, z)
        writer.SetFileName(contour_name)
        writer.SetInputData(poly)
        writer.Write()
        os.system('sed -i "1s/4.1/4.0/" {0}'.format(contour_name))


def evaluate_strain_by_length(contour_name_stem, T, dt, output_name_stem):
    """ Calculate the strain based on the line length """
    # Read the polydata at the first time frame (ED frame)
    fr = 0
    reader = vtk.vtkPolyDataReader()
    reader.SetFileName('{0}{1:02d}.vtk'.format(contour_name_stem, fr))
    reader.Update()
    poly = reader.GetOutput()
    points = poly.GetPoints()

    # Calculate the length of each line
    lines = poly.GetLines()
    lines_aha = poly.GetCellData().GetArray('Segment ID')
    lines_dir = poly.GetCellData().GetArray('Direction ID')
    n_lines = lines.GetNumberOfCells()
    length_ED = np.zeros(n_lines)
    seg_id = np.zeros(n_lines)
    dir_id = np.zeros(n_lines)

    lines.InitTraversal()
    for i in range(n_lines):
        ids = vtk.vtkIdList()
        lines.GetNextCell(ids)
        p1 = np.array(points.GetPoint(ids.GetId(0)))
        p2 = np.array(points.GetPoint(ids.GetId(1)))
        d = np.linalg.norm(p1 - p2)
        seg_id[i] = lines_aha.GetValue(i)
        dir_id[i] = lines_dir.GetValue(i)
        length_ED[i] = d

    # For each time frame, calculate the strain, i.e. change of length
    table_strain = {}
    table_strain['radial'] = np.zeros((17, T))
    table_strain['circum'] = np.zeros((17, T))

    for fr in range(0, T):
        # Read the polydata
        reader = vtk.vtkPolyDataReader()
        filename = '{0}{1:02d}.vtk'.format(contour_name_stem, fr)
        reader.SetFileName(filename)
        reader.Update()
        poly = reader.GetOutput()
        points = poly.GetPoints()

        # Calculate the strain for each line
        lines = poly.GetLines()
        n_lines = lines.GetNumberOfCells()
        strain = np.zeros(n_lines)
        vtk_strain = vtk.vtkFloatArray()
        vtk_strain.SetName('Strain')
        lines.InitTraversal()
        for i in range(n_lines):
            ids = vtk.vtkIdList()
            lines.GetNextCell(ids)
            p1 = np.array(points.GetPoint(ids.GetId(0)))
            p2 = np.array(points.GetPoint(ids.GetId(1)))
            d = np.linalg.norm(p1 - p2)

            # Strain of this line (unit: %)
            strain[i] = (d - length_ED[i]) / length_ED[i] * 100
            vtk_strain.InsertNextTuple1(strain[i])

        # Save the strain array to the vtk file
        poly.GetCellData().AddArray(vtk_strain)
        writer = vtk.vtkPolyDataWriter()
        writer.SetInputData(poly)
        writer.SetFileName(filename)
        writer.Write()
        os.system('sed -i "1s/4.1/4.0/" {0}'.format(filename))

        # Calculate the segmental and global strains
        for i in range(0, 16):
            table_strain['radial'][i, fr] = np.mean(strain[(seg_id == (i + 1)) & (dir_id == 1)])
            table_strain['circum'][i, fr] = np.mean(strain[(seg_id == (i + 1)) & (dir_id == 2)])
        table_strain['radial'][-1, fr] = np.mean(strain[dir_id == 1])
        table_strain['circum'][-1, fr] = np.mean(strain[dir_id == 2])

    for c in ['radial', 'circum']:
        # Save into csv files
        index = [str(x) for x in np.arange(1, 17)] + ['Global']
        column = np.arange(0, T) * dt * 1e3
        df = pd.DataFrame(table_strain[c], index=index, columns=column)
        df.to_csv('{0}_{1}.csv'.format(output_name_stem, c))


def cine_2d_sa_motion_and_strain_analysis(data_dir, par_dir, output_dir, output_name_stem):
    """ Perform motion tracking and strain analysis for cine MR images. """
    # Crop the image to save computation for image registration
    # Focus on the left ventricle so that motion tracking is less affected by
    # the movement of RV and LV outflow tract
    padding('{0}/seg_sa_ED.nii.gz'.format(data_dir),
            '{0}/seg_sa_ED.nii.gz'.format(data_dir),
            '{0}/seg_sa_lv_ED.nii.gz'.format(output_dir), 3, 0)
    auto_crop_image('{0}/seg_sa_lv_ED.nii.gz'.format(output_dir),
                    '{0}/seg_sa_lv_crop_ED.nii.gz'.format(output_dir), 20)
    os.system('mirtk transform-image {0}/sa.nii.gz {1}/sa_crop.nii.gz '
              '-target {1}/seg_sa_lv_crop_ED.nii.gz'.format(data_dir, output_dir))
    os.system('mirtk transform-image {0}/seg_sa.nii.gz {1}/seg_sa_crop.nii.gz '
              '-target {1}/seg_sa_lv_crop_ED.nii.gz'.format(data_dir, output_dir))

    # Extract the myocardial contours for three slices, respectively basal, mid-cavity and apical
    extract_myocardial_contour('{0}/seg_sa_ED.nii.gz'.format(data_dir),
                               '{0}/myo_contour_ED_z'.format(output_dir),
                               three_slices=True)

    # Split the volume into slices
    split_volume('{0}/sa_crop.nii.gz'.format(output_dir), '{0}/sa_crop_z'.format(output_dir))
    split_volume('{0}/seg_sa_crop.nii.gz'.format(output_dir), '{0}/seg_sa_crop_z'.format(output_dir))

    # Label class in the segmentation
    label = {'BG': 0, 'LV': 1, 'Myo': 2, 'RV': 3}

    # Inter-frame motion estimation
    nim = nib.load('{0}/sa_crop.nii.gz'.format(output_dir))
    Z = nim.header['dim'][3]    # slice
    T = nim.header['dim'][4]    # time(cine)
    dt = nim.header['pixdim'][4]
    dice_lv_myo = []
    for z in range(Z):
        if not os.path.exists('{0}/myo_contour_ED_z{1:02d}.vtk'.format(output_dir, z)):
            continue

        # Split the cine sequence for this slice
        split_sequence('{0}/sa_crop_z{1:02d}.nii.gz'.format(output_dir, z),
                       '{0}/sa_crop_z{1:02d}_fr'.format(output_dir, z))

        # Forward image registration
        for fr in range(1, T):
            target_fr = fr - 1
            source_fr = fr
            target = '{0}/sa_crop_z{1:02d}_fr{2:02d}.nii.gz'.format(output_dir, z, target_fr)
            source = '{0}/sa_crop_z{1:02d}_fr{2:02d}.nii.gz'.format(output_dir, z, source_fr)
            par = '{0}/ffd_cine_2d_motion.cfg'.format(par_dir)
            dof = '{0}/ffd_z{1:02d}_pair_{2:02d}_to_{3:02d}.dof.gz'.format(output_dir, z, target_fr, source_fr)
            os.system('mirtk register {0} {1} -parin {2} -dofout {3}'.format(target, source, par, dof))

        # Compose forward inter-frame transformation fields
        os.system('cp {0}/ffd_z{1:02d}_pair_00_to_01.dof.gz '
                  '{0}/ffd_z{1:02d}_forward_00_to_01.dof.gz'.format(output_dir, z))
        for fr in range(2, T):
            dofs = ''
            for k in range(1, fr + 1):
                dof = '{0}/ffd_z{1:02d}_pair_{2:02d}_to_{3:02d}.dof.gz'.format(output_dir, z, k - 1, k)
                dofs += dof + ' '
            dof_out = '{0}/ffd_z{1:02d}_forward_00_to_{2:02d}.dof.gz'.format(output_dir, z, fr)
            os.system('mirtk compose-dofs {0} {1} -approximate'.format(dofs, dof_out))

        # Backward image registration
        for fr in range(T - 1, 0, -1):
            target_fr = (fr + 1) % T
            source_fr = fr
            target = '{0}/sa_crop_z{1:02d}_fr{2:02d}.nii.gz'.format(output_dir, z, target_fr)
            source = '{0}/sa_crop_z{1:02d}_fr{2:02d}.nii.gz'.format(output_dir, z, source_fr)
            par = '{0}/ffd_cine_2d_motion.cfg'.format(par_dir)
            dof = '{0}/ffd_z{1:02d}_pair_{2:02d}_to_{3:02d}.dof.gz'.format(output_dir, z, target_fr, source_fr)
            os.system('mirtk register {0} {1} -parin {2} -dofout {3}'.format(target, source, par, dof))

        # Compose backward inter-frame transformation fields
        os.system('cp {0}/ffd_z{1:02d}_pair_00_to_{2:02d}.dof.gz '
                  '{0}/ffd_z{1:02d}_backward_00_to_{2:02d}.dof.gz'.format(output_dir, z, T - 1))
        for fr in range(T - 2, 0, -1):
            dofs = ''
            for k in range(T - 1, fr - 1, -1):
                dof = '{0}/ffd_z{1:02d}_pair_{2:02d}_to_{3:02d}.dof.gz'.format(output_dir, z,
                                                                               (k + 1) % T, k)
                dofs += dof + ' '
            dof_out = '{0}/ffd_z{1:02d}_backward_00_to_{2:02d}.dof.gz'.format(output_dir, z, fr)
            os.system('mirtk compose-dofs {0} {1} -approximate'.format(dofs, dof_out))

        # Average the forward and backward transformations
        os.system('mirtk init-dof {0}/ffd_z{1:02d}_forward_00_to_00.dof.gz'.format(output_dir, z))
        os.system('mirtk init-dof {0}/ffd_z{1:02d}_backward_00_to_00.dof.gz'.format(output_dir, z))
        os.system('mirtk init-dof {0}/ffd_z{1:02d}_00_to_00.dof.gz'.format(output_dir, z))
        for fr in range(1, T):
            dof_forward = '{0}/ffd_z{1:02d}_forward_00_to_{2:02d}.dof.gz'.format(output_dir, z, fr)
            weight_forward = float(T - fr) / T
            dof_backward = '{0}/ffd_z{1:02d}_backward_00_to_{2:02d}.dof.gz'.format(output_dir, z, fr)
            weight_backward = float(fr) / T
            dof_combine = '{0}/ffd_z{1:02d}_00_to_{2:02d}.dof.gz'.format(output_dir, z, fr)
            print('average_3d_ffd 2 {0} {1} {2} {3} {4}'.format(dof_forward, weight_forward,
                                                                    dof_backward, weight_backward,
                                                                    dof_combine))
            os.system('average_3d_ffd 2 {0} {1} {2} {3} {4}'.format(dof_forward, weight_forward,
                                                                    dof_backward, weight_backward,
                                                                    dof_combine))

        # Transform the contours
        for fr in range(0, T):
            os.system('mirtk transform-points {0}/myo_contour_ED_z{1:02d}.vtk '
                      '{0}/myo_contour_z{1:02d}_fr{2:02d}.vtk '
                      '-dofin {0}/ffd_z{1:02d}_00_to_{2:02d}.dof.gz'.format(output_dir, z, fr))

        # Transform the segmentation and evaluate the Dice metric
        eval_dice = False
        if eval_dice:
            split_sequence('{0}/seg_sa_crop_z{1:02d}.nii.gz'.format(output_dir, z),
                           '{0}/seg_sa_crop_z{1:02d}_fr'.format(output_dir, z))

            image_names = []
            for fr in range(0, T):
                os.system('mirtk transform-image {0}/seg_sa_crop_z{1:02d}_fr{2:02d}.nii.gz '
                          '{0}/seg_sa_crop_warp_ffd_z{1:02d}_fr{2:02d}.nii.gz '
                          '-dofin {0}/ffd_z{1:02d}_00_to_{2:02d}.dof.gz '
                          '-target {0}/seg_sa_crop_z{1:02d}_fr00.nii.gz'.format(output_dir, z, fr))
                image_A = nib.load('{0}/seg_sa_crop_z{1:02d}_fr00.nii.gz'.format(output_dir, z)).get_data()
                image_B = nib.load('{0}/seg_sa_crop_warp_ffd_z{1:02d}_fr{2:02d}.nii.gz'.format(output_dir, z, fr)).get_data()
                dice_lv_myo += [[np_categorical_dice(image_A, image_B, 1),
                                 np_categorical_dice(image_A, image_B, 2)]]
                image_names += ['{0}/seg_sa_crop_warp_ffd_z{1:02d}_fr{2:02d}.nii.gz'.format(output_dir, z, fr)]
            combine_name = '{0}/seg_sa_crop_warp_ffd_z{1:02d}.nii.gz'.format(output_dir, z)
            make_sequence(image_names, dt, combine_name)

    if eval_dice:
        print(np.mean(dice_lv_myo, axis=0))
        df_dice = pd.DataFrame(dice_lv_myo)
        df_dice.to_csv('{0}/dice_cine_warp_ffd.csv'.format(output_dir), index=None, header=None)

    # Merge the 2D tracked contours from all the slice
    for fr in range(0, T):
        append = vtk.vtkAppendPolyData()
        reader = {}
        for z in range(Z):
            if not os.path.exists('{0}/myo_contour_z{1:02d}_fr{2:02d}.vtk'.format(output_dir, z, fr)):
                continue
            reader[z] = vtk.vtkPolyDataReader()
            reader[z].SetFileName('{0}/myo_contour_z{1:02d}_fr{2:02d}.vtk'.format(output_dir, z, fr))
            reader[z].Update()
            append.AddInputData(reader[z].GetOutput())
        append.Update()
        writer = vtk.vtkPolyDataWriter()
        writer.SetFileName('{0}/myo_contour_fr{1:02d}.vtk'.format(output_dir, fr))
        writer.SetInputData(append.GetOutput())
        writer.Write()

    # Calculate the strain based on the line length
    evaluate_strain_by_length('{0}/myo_contour_fr'.format(output_dir), T, dt, output_name_stem)


def remove_mitral_valve_points(endo_contour, epi_contour, mitral_plane):
    """ Remove the mitral valve points from the contours and
        start the contours from the point next to the mitral valve plane.
        So connecting the lines will be easier in the next step.
        """
    N = endo_contour.shape[0]
    start_i = 0
    for i in range(N):
        y, x = endo_contour[i]
        prev_y, prev_x = endo_contour[(i - 1) % N]
        if not mitral_plane[x, y] and mitral_plane[prev_x, prev_y]:
            start_i = i
            break
    endo_contour = np.concatenate((endo_contour[start_i:], endo_contour[:start_i]))

    N = endo_contour.shape[0]
    end_i = N
    for i in range(N):
        y, x = endo_contour[i]
        if mitral_plane[x, y]:
            end_i = i
            break
    endo_contour = endo_contour[:end_i]

    N = epi_contour.shape[0]
    start_i = 0
    for i in range(N):
        y, x = epi_contour[i]
        y2, x2 = epi_contour[(i - 1) % N]
        if not mitral_plane[x, y] and mitral_plane[x2, y2]:
            start_i = i
            break
    epi_contour = np.concatenate((epi_contour[start_i:], epi_contour[:start_i]))

    N = epi_contour.shape[0]
    end_i = N
    for i in range(N):
        y, x = epi_contour[i]
        if mitral_plane[x, y]:
            end_i = i
            break
    epi_contour = epi_contour[:end_i]
    return endo_contour, epi_contour


def determine_la_aha_part(seg_la, affine_la, affine_sa):
    """ Extract the mid-line of the left ventricle, record its index
        along the long-axis and determine the part for each index.
    """
    # Label class in the segmentation
    label = {'BG': 0, 'LV': 1, 'Myo': 2, 'RV': 3, 'LA': 4, 'RA': 5}

    # Sort the left ventricle and myocardium points according to their long-axis locations
    lv_myo_points = []
    X, Y = seg_la.shape[:2]
    z = 0
    for y in range(Y):
        for x in range(X):
            if seg_la[x, y] == label['LV'] or seg_la[x, y] == label['Myo']:
                z_sa = np.dot(np.linalg.inv(affine_sa), np.dot(affine_la, np.array([x, y, z, 1])))[2]
                la_idx = int(round(z_sa * 2))
                lv_myo_points += [[x, y, la_idx]]
    lv_myo_points = np.array(lv_myo_points)
    lv_myo_idx_min = np.min(lv_myo_points[:, 2])
    lv_myo_idx_max = np.max(lv_myo_points[:, 2])

    # Determine the AHA part according to the slice location along the long-axis
    if affine_sa[2, 2] > 0:
        la_idx = np.arange(lv_myo_idx_max, lv_myo_idx_min, -1)
    else:
        la_idx = np.arange(lv_myo_idx_min, lv_myo_idx_max + 1, 1)

    n_la_idx = len(la_idx)
    i1 = int(math.ceil(n_la_idx / 3.0))
    i2 = int(math.ceil(2 * n_la_idx / 3.0))
    i3 = n_la_idx

    part_z = {}
    for i in range(0, i1):
        part_z[la_idx[i]] = 'basal'

    for i in range(i1, i2):
        part_z[la_idx[i]] = 'mid'

    for i in range(i2, i3):
        part_z[la_idx[i]] = 'apical'

    # Extract the mid-line of left ventricle endocardium.
    # Only use the endocardium points so that it would not be affected by
    # the myocardium points at the most basal slices.
    lv_points = []
    X, Y = seg_la.shape[:2]
    z = 0
    for y in range(Y):
        for x in range(X):
            if seg_la[x, y] == label['LV']:
                z_sa = np.dot(np.linalg.inv(affine_sa), np.dot(affine_la, np.array([x, y, z, 1])))[2]
                la_idx = int(round(z_sa * 2))
                lv_points += [[x, y, la_idx]]
    lv_points = np.array(lv_points)
    lv_idx_min = np.min(lv_points[:, 2])
    lv_idx_max = np.max(lv_points[:, 2])

    mid_line = {}
    for la_idx in range(lv_idx_min, lv_idx_max + 1):
        mx, my = np.mean(lv_points[lv_points[:, 2] == la_idx, :2], axis=0)
        mid_line[la_idx] = np.dot(affine_la, np.array([mx, my, z, 1]))[:3]

    for la_idx in range(lv_myo_idx_min, lv_idx_min):
        mid_line[la_idx] = mid_line[lv_idx_min]

    for la_idx in range(lv_idx_max, lv_myo_idx_max + 1):
        mid_line[la_idx] = mid_line[lv_idx_max]
    return part_z, mid_line


def determine_la_aha_segment_id(point, la_idx, axis, mid_line, part_z):
    """ Determine the AHA segment ID given a point on long-axis images.
        """
    # The mid-point at this position
    mid_point = mid_line[la_idx]

    # The line from the mid-point to the contour point
    vec = point - mid_point
    if np.dot(vec, axis['lv_to_sep']) > 0:
        # This is spetum
        if part_z[la_idx] == 'basal':
            # basal septal
            seg_id = 1
        elif part_z[la_idx] == 'mid':
            # mid septal
            seg_id = 3
        elif part_z[la_idx] == 'apical':
            # apical septal
            seg_id = 5
    else:
        # This is lateral
        if part_z[la_idx] == 'basal':
            # basal lateral
            seg_id = 2
        elif part_z[la_idx] == 'mid':
            # mid lateral
            seg_id = 4
        elif part_z[la_idx] == 'apical':
            # apical lateral
            seg_id = 6
    return seg_id


def extract_la_myocardial_contour(seg_la_name, seg_sa_name, contour_name):
    """ Extract the myocardial contours on long-axis images.
        Also, determine the AHA segment ID for all the contour points.
        """
    # Read the segmentation image
    nim = nib.load(seg_la_name)
    X, Y, Z = nim.header['dim'][1:4]
    affine = nim.affine
    seg = nim.get_data()

    # Label class in the segmentation
    label = {'BG': 0, 'LV': 1, 'Myo': 2, 'RV': 3, 'LA': 4, 'RA': 5}

    # Determine the AHA coordinate system using the mid-cavity slice of short-axis images
    nim_sa = nib.load(seg_sa_name)
    affine_sa = nim_sa.affine
    seg_sa = nim_sa.get_data()
    aha_axis = determine_aha_coordinate_system(seg_sa, affine_sa)

    # Construct the points set and data arrays to represent both endo and epicardial contours
    points = vtk.vtkPoints()
    points_radial = vtk.vtkFloatArray()
    points_radial.SetName('Direction_Radial')
    points_radial.SetNumberOfComponents(3)
    points_label = vtk.vtkIntArray()
    points_label.SetName('Label')
    points_aha = vtk.vtkIntArray()
    points_aha.SetName('Segment ID')
    point_id = 0
    lines = vtk.vtkCellArray()
    lines_aha = vtk.vtkIntArray()
    lines_aha.SetName('Segment ID')
    lines_dir = vtk.vtkIntArray()
    lines_dir.SetName('Direction ID')

    # Check whether there is the endocardial segmentation
    # Only keep the largest connected component
    z = 0
    seg_z = seg[:, :, z]
    endo = (seg_z == label['LV']).astype(np.uint8)
    endo = get_largest_cc(endo).astype(np.uint8)
    # The myocardium may be split to two parts due to the very thin apex.
    # So we do not apply get_largest_cc() to it. However, we remove small pieces, which
    # may cause problems in determining the contours.
    myo = (seg_z == label['Myo']).astype(np.uint8)
    myo = remove_small_cc(myo).astype(np.uint8)
    epi = (endo | myo).astype(np.uint8)
    epi = get_largest_cc(epi).astype(np.uint8)

    # Extract endocardial contour
    # Note: cv2 considers an input image as a Y x X array, which is different
    # from nibabel which assumes a X x Y array.
    _, contours, _ = cv2.findContours(cv2.inRange(endo, 1, 1), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    endo_contour = contours[0][:, 0, :]

    # Extract epicardial contour
    _, contours, _ = cv2.findContours(cv2.inRange(epi, 1, 1), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    epi_contour = contours[0][:, 0, :]

    # Record the points located on the mitral valve plane.
    mitral_plane = np.zeros(seg_z.shape)
    N = epi_contour.shape[0]
    for i in range(N):
        y, x = epi_contour[i]
        if endo[x, y]:
            mitral_plane[x, y] = 1

    # Remove the mitral valve points from the contours and
    # start the contours from the point next to the mitral valve plane.
    # So connecting the lines will be easier in the next step.
    if np.sum(mitral_plane) >= 1:
        endo_contour, epi_contour = remove_mitral_valve_points(endo_contour, epi_contour, mitral_plane)

    # Note that remove_mitral_valve_points may fail if the endo or epi has more
    # than one connected components. As a result, the endo_contour or epi_contour
    # may only have zero or one points left, which cause problems for approximate_contour.

    # Smooth the contours
    if len(endo_contour) >= 2:
        endo_contour = approximate_contour(endo_contour)
    if len(epi_contour) >= 2:
        epi_contour = approximate_contour(epi_contour)

    # Determine the aha part and extract the mid-line of the left ventricle
    part_z, mid_line = determine_la_aha_part(seg_z, affine, affine_sa)
    la_idx_min = np.array([x for x in part_z.keys()]).min()
    la_idx_max = np.array([x for x in part_z.keys()]).max()

    # Go through the endo contour points
    N = endo_contour.shape[0]
    for i in range(N):
        y, x = endo_contour[i]

        # The world coordinate of this point
        p = np.dot(affine, np.array([x, y, z, 1]))[:3]
        points.InsertNextPoint(p[0], p[1], p[2])

        # The index along the long axis
        z_sa = np.dot(np.linalg.inv(affine_sa), np.hstack([p, 1]))[2]
        la_idx = int(round(z_sa * 2))
        la_idx = max(la_idx, la_idx_min)
        la_idx = min(la_idx, la_idx_max)

        # The radial direction
        mid_point = mid_line[la_idx]
        d = p - mid_point
        d = d / np.linalg.norm(d)
        points_radial.InsertNextTuple3(d[0], d[1], d[2])

        # Record the type of the point (1 = endo, 2 = epi)
        points_label.InsertNextTuple1(1)

        # Record the segment ID
        seg_id = determine_la_aha_segment_id(p, la_idx, aha_axis, mid_line, part_z)
        points_aha.InsertNextTuple1(seg_id)

        # Add the line
        if i < (N - 1):
            lines.InsertNextCell(2, [point_id, point_id + 1])
            lines_aha.InsertNextTuple1(seg_id)

            # Line direction (1 = radial, 2 = circumferential, 3 = longitudinal)
            lines_dir.InsertNextTuple1(3)

        # Increment the point index
        point_id += 1

    # Go through the epi contour points
    N = epi_contour.shape[0]
    for i in range(N):
        y, x = epi_contour[i]

        # The world coordinate of this point
        p = np.dot(affine, np.array([x, y, z, 1]))[:3]
        points.InsertNextPoint(p[0], p[1], p[2])

        # The index along the long axis
        z_sa = np.dot(np.linalg.inv(affine_sa), np.hstack([p, 1]))[2]
        la_idx = int(round(z_sa * 2))
        la_idx = max(la_idx, la_idx_min)
        la_idx = min(la_idx, la_idx_max)

        # The radial direction
        mid_point = mid_line[la_idx]
        d = p - mid_point
        d = d / np.linalg.norm(d)
        points_radial.InsertNextTuple3(d[0], d[1], d[2])

        # Record the type of the point (1 = endo, 2 = epi)
        points_label.InsertNextTuple1(2)

        # Record the segment ID
        seg_id = determine_la_aha_segment_id(p, la_idx, aha_axis, mid_line, part_z)
        points_aha.InsertNextTuple1(seg_id)

        # Add the line
        if i < (N - 1):
            lines.InsertNextCell(2, [point_id, point_id + 1])
            lines_aha.InsertNextTuple1(seg_id)

            # Line direction (1 = radial, 2 = circumferential, 3 = longitudinal)
            lines_dir.InsertNextTuple1(3)

        # Increment the point index
        point_id += 1

    # Save to a vtk file
    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.GetPointData().AddArray(points_label)
    poly.GetPointData().AddArray(points_aha)
    poly.GetPointData().AddArray(points_radial)
    poly.SetLines(lines)
    poly.GetCellData().AddArray(lines_aha)
    poly.GetCellData().AddArray(lines_dir)

    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(contour_name)
    writer.SetInputData(poly)
    writer.Write()

    # Change vtk file version to 4.0 to avoid the warning by MIRTK, which is
    # developed using VTK 6.3, which does not know file version 4.1.
    os.system('sed -i "1s/4.1/4.0/" {0}'.format(contour_name))


def evaluate_la_strain_by_length(contour_name_stem, T, dt, output_name_stem):
    """ Calculate the strain based on the line length """
    # Read the polydata at the first time frame (ED frame)
    fr = 0
    reader = vtk.vtkPolyDataReader()
    reader.SetFileName('{0}{1:02d}.vtk'.format(contour_name_stem, fr))
    reader.Update()
    poly = reader.GetOutput()
    points = poly.GetPoints()

    # Calculate the length of each line
    lines = poly.GetLines()
    lines_aha = poly.GetCellData().GetArray('Segment ID')
    lines_dir = poly.GetCellData().GetArray('Direction ID')
    n_lines = lines.GetNumberOfCells()
    length_ED = np.zeros(n_lines)
    seg_id = np.zeros(n_lines)
    dir_id = np.zeros(n_lines)

    lines.InitTraversal()
    for i in range(n_lines):
        ids = vtk.vtkIdList()
        lines.GetNextCell(ids)
        p1 = np.array(points.GetPoint(ids.GetId(0)))
        p2 = np.array(points.GetPoint(ids.GetId(1)))
        d = np.linalg.norm(p1 - p2)
        seg_id[i] = lines_aha.GetValue(i)
        dir_id[i] = lines_dir.GetValue(i)
        length_ED[i] = d

    # For each time frame, calculate the strain, i.e. change of length
    table_strain = {}
    table_strain['longit'] = np.zeros((7, T))

    for fr in range(0, T):
        # Read the polydata
        reader = vtk.vtkPolyDataReader()
        filename = '{0}{1:02d}.vtk'.format(contour_name_stem, fr)
        reader.SetFileName(filename)
        reader.Update()
        poly = reader.GetOutput()
        points = poly.GetPoints()

        # Calculate the strain for each line
        lines = poly.GetLines()
        n_lines = lines.GetNumberOfCells()
        strain = np.zeros(n_lines)
        vtk_strain = vtk.vtkFloatArray()
        vtk_strain.SetName('Strain')
        lines.InitTraversal()
        for i in range(n_lines):
            ids = vtk.vtkIdList()
            lines.GetNextCell(ids)
            p1 = np.array(points.GetPoint(ids.GetId(0)))
            p2 = np.array(points.GetPoint(ids.GetId(1)))
            d = np.linalg.norm(p1 - p2)

            # Strain of this line (unit: %)
            strain[i] = (d - length_ED[i]) / length_ED[i] * 100
            vtk_strain.InsertNextTuple1(strain[i])

        # Save the strain array to the vtk file
        poly.GetCellData().AddArray(vtk_strain)
        writer = vtk.vtkPolyDataWriter()
        writer.SetInputData(poly)
        writer.SetFileName(filename)
        writer.Write()
        os.system('sed -i "1s/4.1/4.0/" {0}'.format(filename))

        # Calculate the segmental and global strains
        for i in range(6):
            table_strain['longit'][i, fr] = np.mean(strain[(seg_id == (i + 1)) & (dir_id == 3)])
        table_strain['longit'][-1, fr] = np.mean(strain[dir_id == 3])

    for c in ['longit']:
        # Save into csv files
        index = [str(x) for x in np.arange(1, 7)] + ['Global']
        column = np.arange(0, T) * dt * 1e3
        df = pd.DataFrame(table_strain[c], index=index, columns=column)
        df.to_csv('{0}_{1}.csv'.format(output_name_stem, c))


def cine_2d_la_motion_and_strain_analysis(data_dir, par_dir, output_dir, output_name_stem):
    """ Perform motion tracking and strain analysis for cine MR images. """
    # Crop the image to save computation for image registration
    # Focus on the left ventricle so that motion tracking is less affected by
    # the movement of RV and LV outflow tract
    padding('{0}/seg_la_4ch_ED.nii.gz'.format(data_dir),
            '{0}/seg_la_4ch_ED.nii.gz'.format(data_dir),
            '{0}/seg_la_4ch_lv_ED.nii.gz'.format(output_dir), 2, 1)
    padding('{0}/seg_la_4ch_lv_ED.nii.gz'.format(output_dir),
            '{0}/seg_la_4ch_lv_ED.nii.gz'.format(output_dir),
            '{0}/seg_la_4ch_lv_ED.nii.gz'.format(output_dir), 3, 0)
    padding('{0}/seg_la_4ch_lv_ED.nii.gz'.format(output_dir),
            '{0}/seg_la_4ch_lv_ED.nii.gz'.format(output_dir),
            '{0}/seg_la_4ch_lv_ED.nii.gz'.format(output_dir), 4, 0)
    padding('{0}/seg_la_4ch_lv_ED.nii.gz'.format(output_dir),
            '{0}/seg_la_4ch_lv_ED.nii.gz'.format(output_dir),
            '{0}/seg_la_4ch_lv_ED.nii.gz'.format(output_dir), 5, 0)
    auto_crop_image('{0}/seg_la_4ch_lv_ED.nii.gz'.format(output_dir),
                    '{0}/seg_la_4ch_lv_crop_ED.nii.gz'.format(output_dir), 20)
    os.system('mirtk transform-image {0}/la_4ch.nii.gz {1}/la_4ch_crop.nii.gz '
              '-target {1}/seg_la_4ch_lv_crop_ED.nii.gz'.format(data_dir, output_dir))
    os.system('mirtk transform-image {0}/seg_la_4ch.nii.gz {1}/seg_la_4ch_crop.nii.gz '
              '-target {1}/seg_la_4ch_lv_crop_ED.nii.gz'.format(data_dir, output_dir))

    # Extract the myocardial contour
    extract_la_myocardial_contour('{0}/seg_la_4ch_ED.nii.gz'.format(data_dir),
                                  '{0}/seg_sa_ED.nii.gz'.format(data_dir),
                                  '{0}/la_4ch_myo_contour_ED.vtk'.format(output_dir))

    # Inter-frame motion estimation
    nim = nib.load('{0}/la_4ch_crop.nii.gz'.format(output_dir))
    T = nim.header['dim'][4]
    dt = nim.header['pixdim'][4]

    # Label class in the segmentation
    label = {'BG': 0, 'LV': 1, 'Myo': 2, 'RV': 3, 'LA': 4, 'RA': 5}

    # Split the cine sequence
    split_sequence('{0}/la_4ch_crop.nii.gz'.format(output_dir),
                   '{0}/la_4ch_crop_fr'.format(output_dir))

    # Forward image registration
    for fr in range(1, T):
        target_fr = fr - 1
        source_fr = fr
        target = '{0}/la_4ch_crop_fr{1:02d}.nii.gz'.format(output_dir, target_fr)
        source = '{0}/la_4ch_crop_fr{1:02d}.nii.gz'.format(output_dir, source_fr)
        par = '{0}/ffd_cine_la_2d_motion.cfg'.format(par_dir)
        dof = '{0}/ffd_la_4ch_pair_{1:02d}_to_{2:02d}.dof.gz'.format(output_dir, target_fr, source_fr)
        os.system('mirtk register {0} {1} -parin {2} -dofout {3}'.format(target, source, par, dof))

    # Compose forward inter-frame transformation fields
    os.system('cp {0}/ffd_la_4ch_pair_00_to_01.dof.gz '
              '{0}/ffd_la_4ch_forward_00_to_01.dof.gz'.format(output_dir))
    for fr in range(2, T):
        dofs = ''
        for k in range(1, fr + 1):
            dof = '{0}/ffd_la_4ch_pair_{1:02d}_to_{2:02d}.dof.gz'.format(output_dir, k - 1, k)
            dofs += dof + ' '
        dof_out = '{0}/ffd_la_4ch_forward_00_to_{1:02d}.dof.gz'.format(output_dir, fr)
        os.system('mirtk compose-dofs {0} {1} -approximate'.format(dofs, dof_out))

    # Backward image registration
    for fr in range(T - 1, 0, -1):
        target_fr = (fr + 1) % T
        source_fr = fr
        target = '{0}/la_4ch_crop_fr{1:02d}.nii.gz'.format(output_dir, target_fr)
        source = '{0}/la_4ch_crop_fr{1:02d}.nii.gz'.format(output_dir, source_fr)
        par = '{0}/ffd_cine_la_2d_motion.cfg'.format(par_dir)
        dof = '{0}/ffd_la_4ch_pair_{1:02d}_to_{2:02d}.dof.gz'.format(output_dir, target_fr, source_fr)
        os.system('mirtk register {0} {1} -parin {2} -dofout {3}'.format(target, source, par, dof))

    # Compose backward inter-frame transformation fields
    os.system('cp {0}/ffd_la_4ch_pair_00_to_{1:02d}.dof.gz '
              '{0}/ffd_la_4ch_backward_00_to_{1:02d}.dof.gz'.format(output_dir, T - 1))
    for fr in range(T - 2, 0, -1):
        dofs = ''
        for k in range(T - 1, fr - 1, -1):
            dof = '{0}/ffd_la_4ch_pair_{1:02d}_to_{2:02d}.dof.gz'.format(output_dir, (k + 1) % T, k)
            dofs += dof + ' '
        dof_out = '{0}/ffd_la_4ch_backward_00_to_{1:02d}.dof.gz'.format(output_dir, fr)
        os.system('mirtk compose-dofs {0} {1} -approximate'.format(dofs, dof_out))

    # Average the forward and backward transformations
    os.system('mirtk init-dof {0}/ffd_la_4ch_forward_00_to_00.dof.gz'.format(output_dir))
    os.system('mirtk init-dof {0}/ffd_la_4ch_backward_00_to_00.dof.gz'.format(output_dir))
    os.system('mirtk init-dof {0}/ffd_la_4ch_00_to_00.dof.gz'.format(output_dir))
    for fr in range(1, T):
        dof_forward = '{0}/ffd_la_4ch_forward_00_to_{1:02d}.dof.gz'.format(output_dir, fr)
        weight_forward = float(T - fr) / T
        dof_backward = '{0}/ffd_la_4ch_backward_00_to_{1:02d}.dof.gz'.format(output_dir, fr)
        weight_backward = float(fr) / T
        dof_combine = '{0}/ffd_la_4ch_00_to_{1:02d}.dof.gz'.format(output_dir, fr)
        os.system('average_3d_ffd 2 {0} {1} {2} {3} {4}'.format(dof_forward, weight_forward,
                                                              dof_backward, weight_backward,
                                                              dof_combine))

    # Transform the contours and calculate the strain
    for fr in range(0, T):
        os.system('mirtk transform-points {0}/la_4ch_myo_contour_ED.vtk '
                  '{0}/la_4ch_myo_contour_fr{1:02d}.vtk '
                  '-dofin {0}/ffd_la_4ch_00_to_{1:02d}.dof.gz'.format(output_dir, fr))

    # Calculate the strain based on the line length
    evaluate_la_strain_by_length('{0}/la_4ch_myo_contour_fr'.format(output_dir),
                                 T, dt, output_name_stem)

    # Transform the segmentation and evaluate the Dice metric
    eval_dice = False
    if eval_dice:
        split_sequence('{0}/seg_la_4ch_crop.nii.gz'.format(output_dir),
                       '{0}/seg_la_4ch_crop_fr'.format(output_dir))
        dice_lv_myo = []

        image_names = []
        for fr in range(0, T):
            os.system('mirtk transform-image {0}/seg_la_4ch_crop_fr{1:02d}.nii.gz '
                      '{0}/seg_la_4ch_crop_warp_ffd_fr{1:02d}.nii.gz '
                      '-dofin {0}/ffd_la_4ch_00_to_{1:02d}.dof.gz '
                      '-target {0}/seg_la_4ch_crop_fr00.nii.gz'.format(output_dir, fr))
            image_A = nib.load('{0}/seg_la_4ch_crop_fr00.nii.gz'.format(output_dir)).get_data()
            image_B = nib.load('{0}/seg_la_4ch_crop_warp_ffd_fr{1:02d}.nii.gz'.format(output_dir, fr)).get_data()
            dice_lv_myo += [[np_categorical_dice(image_A, image_B, 1),
                             np_categorical_dice(image_A, image_B, 2)]]
            image_names += ['{0}/seg_la_4ch_crop_warp_ffd_fr{1:02d}.nii.gz'.format(output_dir, fr)]
        combine_name = '{0}/seg_la_4ch_crop_warp_ffd.nii.gz'.format(output_dir)
        make_sequence(image_names, dt, combine_name)

        print(np.mean(dice_lv_myo, axis=0))
        df_dice = pd.DataFrame(dice_lv_myo)
        df_dice.to_csv('{0}/dice_cine_la_4ch_warp_ffd.csv'.format(output_dir), index=None, header=None)


def plot_bulls_eye(data, vmin, vmax, cmap='Reds', color_line='black'):
    """ Plot the bull's eye plot.
        data: values for 16 segments
        """
    if len(data) != 16:
        print('Error: len(data) != 16!')
        exit(0)

    # The cartesian coordinate and the polar coordinate
    x = np.linspace(-1, 1, 201)
    y = np.linspace(-1, 1, 201)
    xx, yy = np.meshgrid(x, y)
    r = np.sqrt(xx * xx + yy * yy)
    theta = np.degrees(np.arctan2(yy, xx))

    # The radius and degree for each segment
    R1, R2, R3, R4 = 1, 0.65, 0.3, 0.0
    rad_deg = {
        1: (R1, R2, 60, 120),
        2: (R1, R2, 120, 180),
        3: (R1, R2, -180, -120),
        4: (R1, R2, -120, -60),
        5: (R1, R2, -60, 0),
        6: (R1, R2, 0, 60),
        7: (R2, R3, 60, 120),
        8: (R2, R3, 120, 180),
        9: (R2, R3, -180, -120),
        10: (R2, R3, -120, -60),
        11: (R2, R3, -60, 0),
        12: (R2, R3, 0, 60),
        13: (R3, R4, 45, 135),
        14: (R3, R4, 135, -135),
        15: (R3, R4, -135, -45),
        16: (R3, R4, -45, 45)
    }

    # Plot the segments
    canvas = np.zeros(xx.shape)
    cx, cy = (np.array(xx.shape) - 1) / 2
    sz = cx

    for i in range(1, 17):
        val = data[i - 1]
        r1, r2, theta1, theta2 = rad_deg[i]
        if theta2 > theta1:
            mask = ((r < r1) & (r >= r2)) & ((theta >= theta1) & (theta < theta2))
        else:
            mask = ((r < r1) & (r >= r2)) & ((theta >= theta1) | (theta < theta2))
        canvas[mask] = val
    plt.imshow(canvas, cmap=cmap, vmin=vmin, vmax=vmax)
    plt.colorbar()
    plt.axis('off')
    plt.gca().invert_yaxis()

    # Plot the circles
    for r in [R1, R2, R3]:
        deg = np.linspace(0, 2 * np.pi, 201)
        circle_x = cx + sz * r * np.cos(deg)
        circle_y = cy + sz * r * np.sin(deg)
        plt.plot(circle_x, circle_y, color=color_line)

    # Plot the lines between segments
    for i in range(1, 17):
        r1, r2, theta1, theta2 = rad_deg[i]
        line_x = cx + sz * np.array([r1, r2]) * np.cos(np.radians(theta1))
        line_y = cy + sz * np.array([r1, r2]) * np.sin(np.radians(theta1))
        plt.plot(line_x, line_y, color=color_line)

    # Plot the indicator for RV insertion points
    for i in [2, 4]:
        r1, r2, theta1, theta2 = rad_deg[i]
        x = cx + sz * r1 * np.cos(np.radians(theta1))
        y = cy + sz * r1 * np.sin(np.radians(theta1))
        plt.plot([x, x - sz * 0.2], [y, y], color=color_line)


def atrium_pass_quality_control(label, label_dict):
    """ Quality control for atrial volume estimation """
    for l_name, l in label_dict.items():
        # Criterion: the atrium does not disappear at any time point so that we can
        # measure the area and length.
        T = label.shape[3]  # 帧数
        for t in range(T):
            label_t = label[:, :, 0, t]
            area = np.sum(label_t == l)
            if area == 0:
                print('The area of {0} is 0 at time frame {1}.'.format(l_name, t))
                return False
    return True


def evaluate_atrial_area_length(label, nim, long_axis):
    """ Evaluate the atrial area and length from 2 chamber or 4 chamber view images. """
    # Area per pixel
    pixdim = nim.header['pixdim'][1:4]
    area_per_pix = pixdim[0] * pixdim[1] * 1e-2  # Unit: cm^2

    # Go through the label class
    L = []
    A = []
    landmarks = []
    labs = np.sort(list(set(np.unique(label)) - set([0])))
    for i in labs:
        # The binary label map
        label_i = (label == i)

        # Get the largest component in case we have a bad segmentation
        label_i = get_largest_cc(label_i)

        # Go through all the points in the atrium, sort them by the distance along the long-axis.
        points_label = np.nonzero(label_i)
        points = []
        for j in range(len(points_label[0])):
            x = points_label[0][j]
            y = points_label[1][j]
            points += [[x, y,
                        np.dot(np.dot(nim.affine, np.array([x, y, 0, 1]))[:3], long_axis)]]
        points = np.array(points)
        points = points[points[:, 2].argsort()]

        # The centre at the top part of the atrium (top third)
        n_points = len(points)
        top_points = points[int(2 * n_points / 3):]
        cx, cy, _ = np.mean(top_points, axis=0)

        # The centre at the bottom part of the atrium (bottom third)
        bottom_points = points[:int(n_points / 3)]
        bx, by, _ = np.mean(bottom_points, axis=0)

        # Determine the major axis by connecting the geometric centre and the bottom centre
        major_axis = np.array([cx - bx, cy - by])
        major_axis = major_axis / np.linalg.norm(major_axis)

        # Get the intersection between the major axis and the atrium contour
        px = cx + major_axis[0] * 100
        py = cy + major_axis[1] * 100
        qx = cx - major_axis[0] * 100
        qy = cy - major_axis[1] * 100

        if np.isnan(px) or np.isnan(py) or np.isnan(qx) or np.isnan(qy):
            return -1, -1, -1

        # Note the difference between nifti image index and cv2 image index
        # nifti image index: XY
        # cv2 image index: YX (height, width)
        image_line = np.zeros(label_i.shape)
        cv2.line(image_line, (int(qy), int(qx)), (int(py), int(px)), (1, 0, 0))
        image_line = label_i & (image_line > 0)

        # Sort the intersection points by the distance along long-axis
        # and calculate the length of the intersection
        points_line = np.nonzero(image_line)
        points = []
        for j in range(len(points_line[0])):
            x = points_line[0][j]
            y = points_line[1][j]
            # World coordinate
            point = np.dot(nim.affine, np.array([x, y, 0, 1]))[:3]
            # Distance along the long-axis
            points += [np.append(point, np.dot(point, long_axis))]
        points = np.array(points)
        if len(points) == 0:
            return -1, -1, -1
        points = points[points[:, 3].argsort(), :3]
        L += [np.linalg.norm(points[-1] - points[0]) * 1e-1]  # Unit: cm

        # Calculate the area
        A += [np.sum(label_i) * area_per_pix]

        # Landmarks of the intersection points
        landmarks += [points[0]]
        landmarks += [points[-1]]
    return A, L, landmarks


def aorta_pass_quality_control(image, seg):
    """ Quality control for aortic segmentation """
    for l_name, l in [('AAo', 1), ('DAo', 2)]:
        # Criterion 1: the aorta does not disappear at some point.
        T = seg.shape[3]
        for t in range(T):
            seg_t = seg[:, :, :, t]
            area = np.sum(seg_t == l)
            if area == 0:
                print('The area of {0} is 0 at time frame {1}.'.format(l_name, t))
                return False

        # Criterion 2: no strong image noise, which affects the segmentation accuracy.
        image_ED = image[:, :, :, 0]
        seg_ED = seg[:, :, :, 0]
        mean_intensity_ED = image_ED[seg_ED == l].mean()
        ratio_thres = 3
        for t in range(T):
            image_t = image[:, :, :, t]
            seg_t = seg[:, :, :, t]
            max_intensity_t = np.max(image_t[seg_t == l])
            ratio = max_intensity_t / mean_intensity_ED
            if ratio >= ratio_thres:
                print('The image becomes very noisy at time frame {0}.'.format(t))
                return False

        # Criterion 3: no fragmented segmentation
        pixel_thres = 10
        for t in range(T):
            seg_t = seg[:, :, :, t]
            cc, n_cc = skimage.measure.label(seg_t == l, neighbors=8, return_num=True)
            count_cc = 0
            for i in range(1, n_cc + 1):
                binary_cc = (cc == i)
                if np.sum(binary_cc) > pixel_thres:
                    # If this connected component has more than certain pixels, count it.
                    count_cc += 1
            if count_cc >= 2:
                print('The segmentation has at least two connected components with more than {0} pixels '
                      'at time frame {1}.'.format(pixel_thres, t))
                return False

        # Criterion 4: no abrupt change of area
        A = np.sum(seg == l, axis=(0, 1, 2))
        for t in range(T):
            ratio = A[t] / float(A[t-1])
            if ratio >= 2 or ratio <= 0.5:
                print('There is abrupt change of area at time frame {0}.'.format(t))
                return False
    return True
