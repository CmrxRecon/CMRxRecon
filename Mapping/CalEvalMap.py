import numpy as np
from scipy.optimize import leastsq
import nibabel as nib
import pandas as pd
import h5py
import os
import copy
import time
import concurrent.futures

from scipy.optimize import curve_fit
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
from cardiac_utils import determine_aha_coordinate_system, determine_aha_part, determine_aha_segment_id
from image_utils import remove_small_cc, get_largest_cc


def error(p,x,y):
    # print(s)
    return func(p,x)-y # x、y should be list, and return a list

def func(p,x):
    k,b=p
    return k*x+b

def t2Relax(numsl, zoom, T2, PD, Rsq, EchoTimes):
    for z in range(0, numsl):
        # t = time.time()
        for y in range(0, zoom.shape[0]):
            for x in range(0, zoom.shape[1]):
                S = np.squeeze(zoom[y, x, z, :])

                if S[1] < 0:
                    T2[y, x, z] = 0
                    PD[y, x, z] = 0
                    Rsq[y, x, z] = 0
                elif S[1] > 10000:
                    T2[y, x, z] = 0
                    PD[y, x, z] = 0
                    Rsq[y, x, z] = 0
                else:
                    # popt = leastsq(func, EchoTimes, args=(np.log(S)))
                    s = " "  # The least squares function leastsq needs to call the error function multiple times to find the values of k and b that minimize the sum of squared errors.
                    p0 = [100, 2]
                    popt = leastsq(error, p0, args=(EchoTimes, np.log(S)))
                    # tmp = EchoTime[0:2]/np.log(S)
                    # T2[y, x, z] = -1/tmp[0]
                    tmp = -1./(popt[0][0]+np.finfo(np.float32).eps)
                    T2[y, x, z] = tmp   #popt[0][0]    #popt[1]
                    PD[y, x, z] = popt[0][1]    #popt[0]
                    Rsq[y, x, z] = 0
                    if T2[y, x, z] > 200:  # show values much closer to the real T2
                        T2[y, x, z] = 0
                        PD[y, x, z] = 0
                        Rsq[y, x, z] = 0
                    elif T2[y, x, z] < 0:
                        T2[y, x, z] = 0
                        PD[y, x, z] = 0
                        Rsq[y, x, z] = 0
        print('Remaining'+str(numsl-z)+'slices')
    return (T2, PD, Rsq)

def CalSaveT2map(T2Recon, invtime_path, target_dir, folder):
    if os.path.isfile(target_dir +'/'+ folder + '/CalT2Reconmap.mat'):
        print('T2 map exists!')
        mat_file = h5py.File(target_dir + '/'+folder + '/CalT2Reconmap.mat', 'r')
        T2ReconMap = mat_file['CalT2Reconmap'][:]
    else:
        data = np.genfromtxt(invtime_path, delimiter=',')  # read .csv file
        row, col, Slc_Num, TI_Num = T2Recon.shape
        invtime = data[1:TI_Num + 1, 1]
        T2ReconMap = np.zeros((int(row), int(col), int(Slc_Num)))
        PD = np.zeros((int(row), int(col), int(Slc_Num)))
        Rsq = np.zeros((int(row), int(col), int(Slc_Num)))
        T2ReconMap, PD, Rsq = t2Relax(int(Slc_Num), T2Recon, T2ReconMap, PD, Rsq, invtime)
        with h5py.File(target_dir + '/'+folder + '/CalT2Reconmap.mat', 'w') as f:
            f.create_dataset('CalT2Reconmap', data=T2ReconMap)
    return T2ReconMap

def func_orig(x, a, b, c):
    return a*(1-np.exp(-b*x)) + c
#
# def fit_curve(args):
#     func, xdata, ydata, p0 = args
#     try:
#         popt, pcov = curve_fit(func, xdata, ydata, p0=p0)
#         yf_est = func(xdata, *popt)
#         sq_err_curr = np.sum((yf_est - ydata) ** 2, dtype=np.float32)
#         return popt, sq_err_curr
#     except RuntimeError:
#         return p0, np.inf

# def calc_t1value(j, ir_img, inversiontime):
#     nx, ny, nti = ir_img.shape
#     inversiontime = np.asarray(inversiontime)
#     r = int(j / ny)
#     c = int(j % ny)
#
#     p0_initial = [350, 0.005, -150]
#
#     y = ir_img[r, c, :]
#     yf = copy.copy(y)
#     sq_err = np.inf
#     curve_fit_success = False
#
#     for nsignflip in range(6):  # Optimize the loop range to 6, as the subsequent symmetric cases can be obtained by reversing the previous ones.
#         yf[:nsignflip+1] = -y[:nsignflip+1]
#
#         pool = Pool()  # creating a process pool
#         func_args = [(func_orig, inversiontime, yf, p0_initial)] * 9
#         results = pool.map(fit_curve, func_args)  # parallel fitting
#
#         for popt, sq_err_curr in results:
#             if sq_err_curr < sq_err:
#                 curve_fit_success = True
#                 sq_err = sq_err_curr
#                 a1_opt, b1_opt, c1_opt = popt
#
#         pool.close()
#         pool.join()
#
#     if not curve_fit_success:
#         a1_opt = 0
#         b1_opt = np.inf
#         c1_opt = 0
#
#     return a1_opt, b1_opt, c1_opt


# def calc_t1value(j, ir_img, inversiontime):
#
#     nx, ny, nti = ir_img.shape
#     inversiontime = np.asarray(inversiontime)
#     y = np.zeros(nti)
#     r = int(j/ny)
#     c = int(j%ny)
#
#     p0_initial = [350, 0.005, -150]
#
#     for tino in range(nti):
#         y[tino] = ir_img[r,c,tino]
#
#     yf = copy.copy(y)
#     sq_err = 100000000.0
#     curve_fit_success = False
#
#     for nsignflip in range(9):
#         if nsignflip == 0:
#             yf[0] = -y[0]
#         elif nsignflip == 1:
#             yf[0:1] = -y[0:1]
#             # yf[1] = -y[1]
#         elif nsignflip == 2:
#             yf[0:2] = -y[0:2]
#             # yf[1] = -y[1]
#             # yf[2] = -y[2]
#         elif nsignflip == 3:
#             yf[0:3] = -y[0:3]
#             # yf[1] = -y[1]
#             # yf[2] = -y[2]
#             # yf[3] = -y[3]
#         elif nsignflip == 4:
#             yf[0:4] = -y[0:4]
#             # yf[1] = -y[1]
#             # yf[2] = -y[2]
#             # yf[3] = -y[3]
#             # yf[4] = -y[4]
#         elif nsignflip == 5:
#             yf[0:5] = -y[0:5]
#             # yf[1] = -y[1]
#             # yf[2] = -y[2]
#             # yf[3] = -y[3]
#             # yf[4] = -y[4]
#             # yf[5] = -y[5]
#         try:
#             popt,pcov = curve_fit(func_orig, inversiontime, yf, p0=p0_initial)
#         except RuntimeError:
#             # print("Error - curve_fit failed")
#             # curve_fit_success = False
#             popt = p0_initial
#
#         a1 = popt[0]
#         b1 = popt[1]
#         c1 = popt[2]
#
#         yf_est = func_orig(inversiontime, a1, b1, c1)
#         sq_err_curr = np.sum((yf_est - yf)**2, dtype=np.float32)
#
#         if sq_err_curr < sq_err:
#             curve_fit_success = True
#             sq_err = sq_err_curr
#             a1_opt = a1
#             b1_opt = b1
#             c1_opt = c1
#
#     if not curve_fit_success:
#         a1_opt = 0
#         b1_opt = np.iinfo(np.float32).max
#         c1_opt = 0
#
#     return a1_opt, b1_opt, c1_opt

# def calculate_T1map(ir_img, inversiontime):
#     print('Coming')
#     nx, ny, nti = ir_img.shape
#     t1map = np.zeros([nx, ny, 3])
#     ir_img = copy.copy(ir_img)
#     if inversiontime[-1] == 0:
#         inversiontime = inversiontime[0:-1]
#         nTI = inversiontime.shape[0]
#         if nti > nTI:
#             ir_img = ir_img[:,:,0:nTI]
#     for j in range(nx*ny):
#         r = int(j / ny)
#         c = int(j % ny)
#         t1map[r, c, :] = calc_t1value(j, ir_img, inversiontime)
#     print('Completed')
#     return t1map

# def CalSaveT1map(T1Recon, invtime_path, target_dir, folder):
#     if os.path.isfile(target_dir + folder + '/CalT1Reconmap.mat'):
#         print('T1 map exists!')
#         mat_file = h5py.File(target_dir + folder + '/CalT1Reconmap.mat', 'r')
#         T1ReconMap = mat_file['CalT1Reconmap'][:]
#     else:
#         row, col, Slc_Num, TI_Num = T1Recon.shape
#         data = np.genfromtxt(invtime_path, delimiter=',')
#         invtime = data[1:TI_Num + 1, 1:Slc_Num + 1]  # [9,5]
#         T1ReconMap = np.zeros((int(row), int(col), int(Slc_Num)))
#         for slc in range(Slc_Num):
#             # Apply calculation
#             ir_img = T1Recon[:, :, slc, :] * 1e6
#             invtime = invtime[:, slc]
#             t1_params_pre = calculate_T1map(ir_img, invtime)
#             a = t1_params_pre[:, :, 0]
#             b = t1_params_pre[:, :, 1]
#             c = t1_params_pre[:, :, 2]
#             t1 = (1 / b) * (a / (a + c) - 1)
#             T1ReconMap[:, :, slc] = t1
#             # creat HDF5 file
#         with h5py.File(target_dir + folder + '/CalT1Reconmap.mat', 'w') as f:
#             f.create_dataset('CalT1Reconmap', data=T1ReconMap)
#     return T1ReconMap

def fit_curve(args):
    func, xdata, ydata, p0 = args
    try:
        popt, pcov = curve_fit(func, xdata, ydata, p0=p0, method='trf')
        yf_est = func(xdata, *popt)
        sq_err_curr = np.sum((yf_est - ydata) ** 2, dtype=np.float32)
        return popt, sq_err_curr
    except RuntimeError:
        return p0, np.inf

def calc_t1value(j, ir_img, inversiontime):
    nx, ny, nti = ir_img.shape
    inversiontime = np.asarray(inversiontime)
    r = int(j / ny)
    c = int(j % ny)

    p0_initial = [350, 0.005, -150]

    y = ir_img[r, c, :]
    yf = copy.copy(y)
    sq_err = np.inf
    curve_fit_success = False

    with ThreadPoolExecutor() as executor:
        for nsignflip in range(6):
            yf[:nsignflip+1] = -y[:nsignflip+1]

            func_args = [(func_orig, inversiontime, yf, p0_initial)] * 9
            results = executor.map(fit_curve, func_args)

            for popt, sq_err_curr in results:
                if sq_err_curr < sq_err:
                    curve_fit_success = True
                    sq_err = sq_err_curr
                    a1_opt, b1_opt, c1_opt = popt

            if curve_fit_success:
                break

    if not curve_fit_success:
        a1_opt = 0
        b1_opt = np.inf
        c1_opt = 0

    return a1_opt, b1_opt, c1_opt

def calculate_T1value(args):
    j, ir_img, inversiontime = args
    nx, ny, nti = ir_img.shape
    r = int(j / ny)
    c = int(j % ny)
    return calc_t1value(j, ir_img, inversiontime)

def calculate_T1map(ir_img, inversiontime):
    nx, ny, nti = ir_img.shape
    t1map = np.zeros([nx, ny, 3])
    ir_img = np.copy(ir_img)
    if inversiontime[-1] == 0:
        inversiontime = inversiontime[0:-1]
        nTI = inversiontime.shape[0]
        if nti > nTI:
            ir_img = ir_img[:,:,0:nTI]
    indices = [(j, ir_img, inversiontime) for j in range(nx*ny)]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(calculate_T1value, indices)

        for j, t1_params in enumerate(results):
            r = int(j / ny)
            c = int(j % ny)
            t1map[r, c, :] = t1_params

    return t1map

def CalSaveT1map(T1Recon, invtime_path, target_dir, folder):
    start_time = time.time()  # record time
    if os.path.isfile(target_dir + folder + '/CalT1Reconmap.mat'):
        print('T1 map exists!')
        mat_file = h5py.File(target_dir + folder + '/CalT1Reconmap.mat', 'r')
        T1ReconMap = mat_file['CalT1Reconmap'][:]
    else:
        row, col, Slc_Num, TI_Num = T1Recon.shape
        data = np.genfromtxt(invtime_path, delimiter=',')
        invtime = data[1:TI_Num + 1, 1:Slc_Num + 1]  # [9,5]
        T1ReconMap = np.zeros((int(row), int(col), int(Slc_Num)))

        ir_img_list = [T1Recon[:, :, slc, :] * 1e6 for slc in range(Slc_Num)]
        invtime_list = [invtime[:, slc] for slc in range(Slc_Num)]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # args_list = zip(ir_img_list, invtime_list)
            # results = executor.map(calculate_T1map, args_list)
            results = executor.map(calculate_T1map, ir_img_list, invtime_list)

            for slc, t1_params_pre in enumerate(results):
                a = t1_params_pre[:, :, 0]
                b = t1_params_pre[:, :, 1]
                c = t1_params_pre[:, :, 2]
                t1 = (1 / b) * (a / (a + c) - 1)
                T1ReconMap[:, :, slc] = t1

        with h5py.File(target_dir + folder + '/CalT1Reconmap.mat', 'w') as f:
            f.create_dataset('CalT1Reconmap', data=T1ReconMap)
    elapsed_time = time.time() - start_time  # calculate processing time
    print("Total time: {:.2f} seconds".format(elapsed_time))
    return T1ReconMap

def EvalMyo(mapping, seg_path, mapping_type, part=None):
    nim = nib.load(seg_path)
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
        x_myo, y_myo = np.where(myo == 1)
        # z_myo = np.ones_like(x_myo)*z
        for x, y in zip(x_myo, y_myo):
            p = np.dot(affine, np.array([x, y, z, 1]))[:3]
            seg_id = determine_aha_segment_id(p, lv_centre, aha_axis, part_z[z])
            aha_mask_z[x, y] = seg_id

        aha_mask[:, :, z] = aha_mask_z

    aha17_mapping = np.zeros(17)  # 17(1-16,and Global mean)
    for i in range(16):
        aha17_mapping[i] = np.mean(mapping[aha_mask == i + 1])

    # print(np.mean(mapping[aha_mask != 0]))
    aha17_mapping[-1] = np.mean(mapping[aha_mask != 0])

    index = [str(x) for x in np.arange(1, 17)] + ['Global' + mapping_type]
    df = pd.DataFrame(aha17_mapping, index=index, columns=['Mapping'])
    return df



