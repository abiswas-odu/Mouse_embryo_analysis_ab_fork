import numpy as np
import pandas as pd
import seaborn as sns
import glob
from skimage import io
import matplotlib.pyplot as plt
from skimage import measure
from skimage.transform import rescale
import h5py
from pyklb import readfull
from Label_read import *

# This method aligns Short camera to Long one, to be used for TF quantification obtained with Cam_Short.
# The code works under the assumption that TF should be localized in the nucleus.

# Parameters:
# # raw_dir = path prefix for raw data (including channel)
# # nucl_segm_dir = directory with nuclear segmentation results
# # time = which time to use for alignment; theoretically, all the timepoints should produce similar results.
# # offset = offset that was used for cropping;
# # max_margin = 2048, original size of images;

#Returns
# # x_shift and y_shift that maximize the signal within the segments found through nuclear segmentation.

def align_cameras(raw_dir, nucl_segm_dir, time = 50, offset = 150, max_margin = 2048):
    vpairs = pd.read_csv(nucl_segm_dir+'/vpairs.csv', index_col = [0])
    hpairs = pd.read_csv(nucl_segm_dir+'/hpairs.csv', index_col = [0]) 
    vpairs = tuple(map(int, vpairs['all'][0][1:-1].split(', ')))
    hpairs = tuple(map(int, hpairs['all'][0][1:-1].split(', ')))
    crop_y_min = max(hpairs[0]-offset,0)
    crop_y_max = min(hpairs[1]+offset, max_margin)
    crop_x_min = max(vpairs[0]-offset,0)
    crop_x_max = min(vpairs[1]+offset, max_margin)
    print('Cropboxes found...')
    
    _, nuc_labels = read_segments('', nucl_segm_dir)
    print('Nuclear Segmentations found...')
    str_time = str(time).zfill(5)
    
    tf = readfull(raw_dir+'/out/folder_Cam_Short_'+str_time+'.lux/klbOut_Cam_Short_'+str_time+'.lux.klb')

    mean_signal = {}
    for x_shift in range(-50, 50):
        mean_signal[x_shift] = {}
        for y_shift in range(-50,50):
            tf_signal = tf[:, 
                     (crop_x_min+x_shift):(crop_x_max+x_shift), 
                     (crop_y_min+y_shift):(crop_y_max+y_shift)]
            mean_signal[x_shift][y_shift] = tf_signal[nuc_labels[time].astype(bool)].mean()
    ind = pd.DataFrame(mean_signal).stack().argmax()
    shs = pd.DataFrame(mean_signal).stack().index[ind]
    x_shift = shs[1]
    y_shift = shs[0]
    print('Alignments found.')
    return x_shift, y_shift
