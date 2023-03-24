import numpy as np
import pandas as pd
from skimage.transform import rescale
from cropbox_loader import load_cropboxes
from Label_read import *
import os
from scipy.ndimage import zoom

# Quantifies TF intensity in cells and nuclei for provided raw images and nuclear segmentation

# Parameters:
# # raw_dir = path prefix for raw data (including channel)
# # nuc_segm_dir = directory with nuclear segmentation results
# # cell_volume_cutoff = cell volume below which cells are not considered;
# # max_time = up to which time you need to quantify;
# # offset = offset that was used for cropping;
# # max_margin = 2048, original size of images;
# # which_cam = which camera to quantify, e.g., ‘Long’ for Yap;
# # x_shift and y_shift can be used for camera alignment. For our 210809 data, for Cdx2, I found x_shift = -11, y_shift = 15.

# Returns:
# # nuc_tf_vals = dictionary of nuclear intensities indexed by (timepoint, label)

def quantify_tf_nucl(nucl_raw_dir, nucl_segm_dir, crop_dir,
                crop_box_index=0, cell_volume_cutoff=0, min_time=0,
                max_time=-1, rescale=False, offset=150,
                max_margin=2048, max_abs_alignment_shift=50, x_shift=0, y_shift=0):

    crop_y_min, crop_y_max, crop_x_min, crop_x_max = load_cropboxes(crop_dir, crop_box_index,
                                                                    offset, max_margin, max_abs_alignment_shift)

    # read TF filenames recursively
    images = [os.path.join(dp, f)
              for dp, dn, filenames in os.walk(nucl_raw_dir)
              for f in filenames if (os.path.splitext(f)[1] == '.klb' or
                                     os.path.splitext(f)[1] == '.h5' or
                                     os.path.splitext(f)[1] == '.tif' or
                                     os.path.splitext(f)[1] == '.npy')]

    nuc_tf_vals = {}
    nuc_vols = {}

    # Set max_time to the len-1 to that we can loop till last
    if max_time == -1:
        max_time = len(images) - 1
    
    # loop through timepoints
    images = np.sort(images)
    for i, im in enumerate(images):
        try:
            image_file_str = str(im)
            print('Processing: ' + image_file_str)
            dir_name = os.path.dirname(image_file_str)
            file_base, file_prefix, file_ext, time_index = get_filename_components(image_file_str)

            if min_time <= time_index < max_time+1:
                a = read_image(image_file_str)
                a = a[:, (crop_x_min+x_shift):(crop_x_max+x_shift), (crop_y_min+y_shift):(crop_y_max+y_shift)]
                # Get the nuclei label file names with same camera
                # read segmentation results
                nuc_label = read_segments(nucl_segm_dir, file_prefix, file_ext, "nuclei")
                #Extract nucl channel data
                if type(nuc_label) is np.ndarray:
                    nuc_label = nuc_label[:, crop_x_min:crop_x_max, crop_y_min:crop_y_max]
                    if rescale:
                        a = rescale(a, (1/(2*0.208), 1/4, 1/4), preserve_range=True, anti_aliasing=True)
                        nuc_label = zoom(nuc_label, (1/(0.208*2), 1/4, 1/4), order=0, mode='nearest')
                    nuc_tf_vals[time_index] = {}
                    nuc_vols[time_index] = {}
                    for lab in np.unique(nuc_label):
                        if lab != 0:
                            nuc_tf_vals[time_index][lab] = np.mean(a[nuc_label == lab])
                            nuc_vols[time_index][lab] = np.count_nonzero(nuc_label == lab)
        except Exception as e:
            print('Skipping image: ' + str(im))
            print('Exception:')
            print(e)
    return nuc_tf_vals, nuc_vols


# Quantifies TF intensity in cells for raw images and corresponding membrane segmentation

# Parameters:
# # raw_dir = path prefix for raw data (including channel)
# # mem_segm_dir = directory with membrane segmentation results
# # cell_volume_cutoff = cell volume below which cells are not considered;
# # max_time = up to which time you need to quantify;
# # offset = offset that was used for cropping;
# # max_margin = 2048, original size of images;
# # which_cam = which camera to quantify, e.g., ‘Long’ for Yap;
# # x_shift and y_shift can be used for camera alignment. For our 210809 data, for Cdx2, I found x_shift = -11, y_shift = 15.

# Returns:
# # mem_tf_vals = dictionary of membrane intensities indexed by (timepoint, label)

def quantify_tf_mebrane(membrane_raw_dir, mem_segm_dir, crop_dir,
                crop_box_index=0, cell_volume_cutoff=0, min_time=0,
                max_time=-1, offset=150,
                max_margin=2048, max_abs_alignment_shift=50, x_shift=0, y_shift=0):

    crop_y_min, crop_y_max, crop_x_min, crop_x_max = load_cropboxes(crop_dir, crop_box_index,
                                                                    offset, max_margin, max_abs_alignment_shift)
    # read TF filenames recursively
    images = [os.path.join(dp, f)
              for dp, dn, filenames in os.walk(membrane_raw_dir)
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
    for i, im in enumerate(images):
        try:
            image_file_str = str(im)
            print('Processing: '+ image_file_str)
            a = read_image(image_file_str)
            a = a[:, (crop_x_min+x_shift):(crop_x_max+x_shift), (crop_y_min+y_shift):(crop_y_max+y_shift)]
            dir_name = os.path.dirname(image_file_str)

            file_base, file_prefix, file_ext, time_index = get_filename_components(image_file_str)

            # Check within range to be extracted
            if time_index >= min_time and time_index < max_time+1:
                #Extract membrane channel data
                mem_label = read_segments(mem_segm_dir, file_prefix, file_ext, "membrane")
                if type(mem_label) is np.ndarray:
                    a_mem = rescale(a, (1/(2*0.208), 1/4, 1/4), preserve_range=True, anti_aliasing=True)
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
    return mem_tf_vals, mem_vols
