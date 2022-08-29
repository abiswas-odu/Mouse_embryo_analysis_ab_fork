import numpy as np
import pandas as pd
from skimage.transform import rescale
from Label_read import *
import os

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


def quantify_tf(raw_dir, mem_segm_dir, nucl_segm_dir, crop_dir,
                crop_box_index=0, cell_volume_cutoff=0, min_time=0,
                max_time=-1, offset=150,
                max_margin=2048, x_shift=0, y_shift=0):
    
    # read cropboxes
    vpairs = pd.read_csv(os.path.join(crop_dir,'vpairs.csv'), index_col=[0])
    hpairs = pd.read_csv(os.path.join(crop_dir,'hpairs.csv'), index_col=[0])
    vpairs = tuple(map(int, vpairs['all'][crop_box_index][1:-1].split(', ')))
    hpairs = tuple(map(int, hpairs['all'][crop_box_index][1:-1].split(', ')))
    crop_y_min = max(hpairs[0]+y_shift-offset,0)
    crop_y_max = min(hpairs[1]+y_shift+offset, max_margin)
    crop_x_min = max(vpairs[0]+x_shift-offset,0)
    crop_x_max = min(vpairs[1]+x_shift+offset, max_margin)
    print('Cropboxes found...')

    # read TF filenames recursively
    images = [os.path.join(dp, f)
              for dp, dn, filenames in os.walk(raw_dir)
              for f in filenames if (os.path.splitext(f)[1] == '.klb' or
                                     os.path.splitext(f)[1] == '.h5' or
                                     os.path.splitext(f)[1] == '.tif' or
                                     os.path.splitext(f)[1] == '.npy')]

    nuc_tf_vals = {}
    nuc_vols = {}
    mem_tf_vals = {}
    mem_vols = {}

    # Set max_time to the len-1 to that we can loop till last
    if max_time == -1:
        max_time = len(images) - 1
    
    # loop through timepoints
    images = np.sort(images)
    for i, im in enumerate(images[min_time:max_time+1]):
        try:
            image_file_str = str(im)
            print('Processing: '+ image_file_str)
            a = read_image(image_file_str)
            a = a[:, crop_x_min:crop_x_max, crop_y_min:crop_y_max]
            dir_name = os.path.dirname(image_file_str)

            cur_name = os.path.basename(image_file_str)
            file_prefix = os.path.splitext(cur_name)[0]
            file_ext = os.path.splitext(cur_name)[1]
            file_base = os.path.basename(cur_name).split(os.extsep)
            time_index = int(file_base[0].split('_')[-1])

            # Get the label file names
            mem_segm_file = os.path.join(mem_segm_dir, file_prefix + "_cp_masks" + file_ext)
            nucl_segm_file = os.path.join(nucl_segm_dir,file_prefix + ".label" + file_ext)
            nucl_segm_file_corrected = os.path.join(nucl_segm_dir,file_prefix + "_SegmentationCorrected" + file_ext)

            # read segmentation results
            mem_label, nuc_label = read_segments(mem_segm_file, nucl_segm_file, nucl_segm_file_corrected)

            #Extract nucl channel data
            if type(nuc_label) is np.ndarray:
                nuc_tf_vals[time_index] = {}
                nuc_vols[time_index] = {}
                nuc_label = nuc_label[:, crop_x_min:crop_x_max, crop_y_min:crop_y_max]
                for lab in np.unique(nuc_label):
                    if lab != 0:
                        nuc_tf_vals[time_index][lab] = np.mean(a[nuc_label == lab])
                        nuc_vols[time_index][lab] = np.count_nonzero(nuc_label == lab)

            #Extract membrane channel data
            if type(mem_label) is np.ndarray:
                a_mem = rescale(a, (1/(2*0.208),1/4,1/4), preserve_range = True, anti_aliasing = True)
                sh = mem_label.shape
                a_mem = a_mem[:sh[0], :sh[1], :sh[2]]
                sh = a_mem.shape
                mem_label = mem_label[:sh[0], :sh[1], :sh[2]]
                mem_tf_vals[time_index] = {}
                mem_vols[time_index] = {}
                for lab in np.unique(mem_label):
                    if lab != 0:
                        if np.sum(mem_label == lab) >= cell_volume_cutoff:
                            mem_tf_vals[time_index][lab] = np.mean(a_mem[mem_label == lab])
                            mem_vols[time_index][lab] = np.count_nonzero(mem_label == lab)
        except Exception as e:
            print('Skipping image: ' + str(im))
            print('Exception:')
            print(e)
    return mem_tf_vals, nuc_tf_vals, mem_vols, nuc_vols

