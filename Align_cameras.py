import pandas as pd
from Label_read import *
from io_utils import read_image, write_image
from cropbox_loader import load_cropboxes

# This method aligns Short camera to Long one, to be used for TF quantification obtained with Cam_Short.
# The code works under the assumption that TF should be localized in the nucleus.

# Parameters:
# # raw_file = path raw data file(including channel)
# # nucl_segm_dir = directory with nuclear segmentation of corresponding time points
# # crop_dir = the directory with the crop data
# # time = which time to use for alignment; theoretically, all the timepoints should produce similar results.
# # offset = offset that was used for cropping;
# # max_margin = 2048, original size of images;

#Returns
# # x_shift and y_shift that maximize the signal within the segments found through nuclear segmentation.


def align_cameras(raw_image, nucl_segm_image, crop_dir, crop_box_index,
                  max_abs_alignment_shift=50, offset=150, max_margin=2048, num_threads: int = 1):

    crop_y_min, crop_y_max, crop_x_min, crop_x_max = load_cropboxes(crop_dir, crop_box_index,
                                                                    offset, max_margin, max_abs_alignment_shift)

    nuc_label = read_image(nucl_segm_image, num_threads)
    nuc_label = nuc_label[:, crop_x_min:crop_x_max, crop_y_min:crop_y_max]
    if type(nuc_label) is np.ndarray:
        print('Nuclear Segmentations found...')
        tf = read_image(raw_image, num_threads)
        mean_signal = {}
        for x_shift in range(-max_abs_alignment_shift, max_abs_alignment_shift):
            mean_signal[x_shift] = {}
            for y_shift in range(-max_abs_alignment_shift, max_abs_alignment_shift):
                try:
                    x_min = (crop_x_min+x_shift) if 0 <= (crop_x_min+x_shift) < max_margin else 0 if 0 > (crop_x_min+x_shift) else max_margin
                    x_max = (crop_x_max+x_shift) if 0 <= (crop_x_max+x_shift) < max_margin else 0 if 0 > (crop_x_max+x_shift) else max_margin
                    y_min = (crop_y_min+y_shift) if 0 <= (crop_y_min+y_shift) < max_margin else 0 if 0 > (crop_y_min+y_shift) else max_margin
                    y_max = (crop_y_max+y_shift) if 0 <= (crop_y_max+y_shift) < max_margin else 0 if 0 > (crop_y_max+y_shift) else max_margin
                    tf_signal = tf[:, x_min:x_max, y_min:y_max]
                    tf_signal_values = tf_signal[nuc_label.astype(bool)]
                    if len(tf_signal_values) > 0:
                        mean_signal[x_shift][y_shift] = tf_signal_values.mean()
                    else:
                        mean_signal[x_shift][y_shift] = 0
                except Exception as e:
                    mean_signal[x_shift][y_shift] = 0
        ind = pd.DataFrame(mean_signal).stack().argmax()
        shs = pd.DataFrame(mean_signal).stack().index[ind]
        x_shift = shs[1]
        y_shift = shs[0]
        return x_shift, y_shift
    else:
        return None, None


def print_aligned(raw_image, nucl_segm_image, crop_dir, crop_box_index, x_shift, y_shift, out_dir,
                  max_abs_alignment_shift=50, offset=150, max_margin=2048, num_threads: int = 1):

    crop_y_min, crop_y_max, crop_x_min, crop_x_max = load_cropboxes(crop_dir, crop_box_index,
                                                                    offset, max_margin, max_abs_alignment_shift)
    nuc_label = read_image(nucl_segm_image, num_threads)
    nuc_label = nuc_label[:, crop_x_min:crop_x_max, crop_y_min:crop_y_max]
    raw_image_name = os.path.splitext(os.path.basename(raw_image))[0]
    raw_image_name = raw_image_name + '_aligned'
    if type(nuc_label) is np.ndarray:

        print('Nuclear Segmentations found...')
        tf = read_image(raw_image, num_threads)

        x_min = (crop_x_min + x_shift) if 0 <= (crop_x_min + x_shift) < max_margin else 0 if 0 > (
                    crop_x_min + x_shift) else max_margin
        x_max = (crop_x_max + x_shift) if 0 <= (crop_x_max + x_shift) < max_margin else 0 if 0 > (
                    crop_x_max + x_shift) else max_margin
        y_min = (crop_y_min + y_shift) if 0 <= (crop_y_min + y_shift) < max_margin else 0 if 0 > (
                    crop_y_min + y_shift) else max_margin
        y_max = (crop_y_max + y_shift) if 0 <= (crop_y_max + y_shift) < max_margin else 0 if 0 > (
                    crop_y_max + y_shift) else max_margin
        tf_signal = tf[:, x_min:x_max, y_min:y_max]
        tf_signal_values = tf_signal[nuc_label.astype(bool)]
        out_image_file = os.path.join(out_dir, raw_image_name)
        write_image(tf_signal_values, out_image_file, 'tif', num_threads)
