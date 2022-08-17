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

# Quantifies TF intensity in cells and nuclei for provided raw images and corresponding membrane and nuclear segmentation

# Parameters:
# # raw_dir = path prefix for raw data (including channel)
# # mem_segm_dir = directory with membrane segmentation results
# # nuc_segm_dir = directory with nuclear segmentation results
# # cell_volume_cutoff = cell volume below which cells are not considered;
# # max_time = up to which time you need to quantify;
# # offset = offset that was used for cropping;
# # max_margin = 2048, original size of images;
# # which_cam = which camera to quantify, e.g., ‘Long’ for Yap;
# # x_shift and y_shift can be used for camera alignment. For our 210809 data, for Cdx2, I found x_shift = -11, y_shift = 15.

# Returns:
# # mem_tf_vals = dictionary of membrane intensities indexed by (timepoint, label)
# # nuc_tf_vals = dictionary of nuclear intensities indexed by (timepoint, label)

# Will return an empty dictionary if one of the segmentation types is unavailable

def quantify_tf(raw_dir, mem_segm_dir, nucl_segm_dir, cell_volume_cutoff = 0, max_time = 120, offset = 150, max_margin = 2048, which_cam = 'Short', x_shift = 0, y_shift = 0):
    
    # read segmentation results
    mem_labels, nuc_labels = read_segments(mem_segm_dir, nucl_segm_dir)
    
    # read cropboxes
    vpairs = pd.read_csv(nucl_segm_dir+'/vpairs.csv', index_col = [0])
    hpairs = pd.read_csv(nucl_segm_dir+'/hpairs.csv', index_col = [0]) 
    vpairs = tuple(map(int, vpairs['all'][0][1:-1].split(', ')))
    hpairs = tuple(map(int, hpairs['all'][0][1:-1].split(', ')))
    crop_y_min = max(hpairs[0]+y_shift-offset,0)
    crop_y_max = min(hpairs[1]+y_shift+offset, max_margin)
    crop_x_min = max(vpairs[0]+x_shift-offset,0)
    crop_x_max = min(vpairs[1]+x_shift+offset, max_margin)
    print('Cropboxes found...')

    # read TF filenames
    tf = glob.glob(raw_dir+'/out/folder_Cam_'+which_cam+'*/klbOut_Cam_'+which_cam+'*.klb')#klbOut_Cam_'+which_cam+'_*.klb')
    #+'/out/folder_Cam_Long*/klbOut_Cam_Long*.klb')

    nuc_tf_vals = {}
    mem_tf_vals = {}
    
    # loop through timepoints
    for i, im in enumerate(np.sort(tf)):
        try:
            print(im)
            a = readfull(str(im))
            a = a[:, crop_x_min:crop_x_max, crop_y_min:crop_y_max]           
            cur_name = im.split('/')[-1]
            #time = int(cur_name.split('.')[0].split('_')[-1])
            time = int(cur_name.split('.')[0].split('_')[-1])
            #print(time)
            if int(time)< max_time:
                cur_num = time
                print(time)  
                nuc_mask = nuc_labels[time]
                sh = nuc_mask.shape
                mem_mask = mem_labels[time]
                #a_mem = zoom(a, (1/(2*0.208),1/4,1/4))
                a_mem = rescale(a, 
                                (1/(2*0.208),1/4,1/4), 
                                preserve_range = True, 
                                anti_aliasing = True)
                sh = mem_mask.shape
                #a_mem = np.swapaxes(a_mem, 1,2)
                a_mem = a_mem[:sh[0], :sh[1], :sh[2]]
                sh = a_mem.shape
                mem_mask = mem_mask[:sh[0], :sh[1], :sh[2]]
                nuc_tf_vals[cur_num] = {}
                mem_tf_vals[cur_num] = {}
                for lab in np.unique(nuc_mask):
                    nuc_tf_vals[cur_num][lab] = np.mean(a[nuc_mask == lab])
                for lab in np.unique(mem_mask):
                    if np.sum(mem_mask == lab)>=cell_volume_cutoff:
                        mem_tf_vals[cur_num][lab] = np.mean(a_mem[mem_mask == lab])
        except:
            print('Skipping image')
            print(im)
            continue

    return mem_tf_vals, nuc_tf_vals

