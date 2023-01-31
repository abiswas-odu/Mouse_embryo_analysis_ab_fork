# erode label images to improve nuclear measurements
# option to draw contours on intensity image
# option to select number of erosion iterations (more implies more erosion)

import tifffile as tiff
import os
import numpy as np
from scipy import ndimage
from GeometricInterpolation import InterpolateTubes, DrawContourForLabel
from io_utils import write_image
from Label_read import *


def erode_image_labels(image_file_str, nucl_segm_dir, out_path, footprint_size = 3, bOutputContourImages = True):
    print('Processing: ', image_file_str)
    try:
        if bOutputContourImages:
            im = read_image(image_file_str)
            # need to make output image rgb to have color contours
            d,h,w = im.shape
            rgb_im = np.zeros([d,h,w,3],dtype=np.uint16) # was 16 if leave original intensities
            rgb_im[:,:,:,0] = im
            rgb_im[:,:,:,1] = im
            rgb_im[:,:,:,2] = im

        # Get the nuclei label file names with same camera
        # read segmentation results
        dir_name = os.path.dirname(image_file_str)
        cur_name = os.path.basename(image_file_str)
        file_prefix = os.path.splitext(cur_name)[0]
        file_ext = os.path.splitext(cur_name)[1]
        file_base = os.path.basename(cur_name).split(os.extsep)
        time_index = int(file_base[0].split('_')[-1])
        label_im = read_segments(nucl_segm_dir, file_prefix, file_ext, "nuclei")

        #Extract nucl channel data
        if type(label_im) is np.ndarray:
            big_label_im = InterpolateTubes(label_im, 10)
            labels = np.unique(label_im)
            nlabels = len(labels) - 1
            new_label_im = np.zeros(big_label_im.shape,dtype=np.uint8)
            print('Number of stardist nuclei:', nlabels)
            for ilabel in labels:
                if ilabel != 0:
                    # make binary image of this mask
                    bin_label_im = np.zeros(big_label_im.shape,dtype=np.bool_)
                    ind = np.where(big_label_im == ilabel)
                    bin_label_im[ind] = 1
                    # erode it
                    struct_elem = np.ones([footprint_size, footprint_size, footprint_size])
                    eroded_im = ndimage.morphology.binary_erosion(bin_label_im, structure=struct_elem, iterations=5)
                    ind = np.where(eroded_im)
                    new_label_im[ind] = ilabel

            # now downsample big_label_im
            final_label_im = new_label_im[::10, :, :]
            if bOutputContourImages:
                for ilabel in labels:
                    if ilabel != 0:
                        # draw label contour on  image
                        # draw on blue channel
                        icolor = (255, 0, 0)  # red
                        rgb_im = DrawContourForLabel(final_label_im, rgb_im, ilabel, icolor)
                # save image with contours
                tiff.imwrite(os.path.join(out_path, 'contours_' + str(time_index) +'.tif'), rgb_im)
            # save new final eroded label image
            final_label_im = np.ascontiguousarray(final_label_im)
            write_image(final_label_im, os.path.join(out_path, file_prefix + ".label"), 'KLB')
    except Exception as e:
        print('Skipping image: ' + str(image_file_str))
        print('Exception:', e)






