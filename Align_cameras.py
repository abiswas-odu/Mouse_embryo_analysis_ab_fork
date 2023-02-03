import numpy as np
import pandas as pd
from Label_read import *
from io_utils import read_image

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


def align_cameras(raw_image, nucl_segm_image, crop_dir, crop_box_index, offset = 150, max_margin = 2048):
    vpairs = pd.read_csv(os.path.join(crop_dir,'vpairs.csv'), index_col = [0])
    hpairs = pd.read_csv(os.path.join(crop_dir,'hpairs.csv'), index_col = [0])
    vpairs = tuple(map(int, vpairs['all'][crop_box_index][1:-1].split(', ')))
    hpairs = tuple(map(int, hpairs['all'][crop_box_index][1:-1].split(', ')))
    crop_y_min = max(hpairs[0]-offset,0)
    crop_y_max = min(hpairs[1]+offset, max_margin)
    crop_x_min = max(vpairs[0]-offset,0)
    crop_x_max = min(vpairs[1]+offset, max_margin)
    print('Cropboxes found...')

    nuc_label = read_image(nucl_segm_image)
    nuc_label = nuc_label[:, crop_x_min:crop_x_max, crop_y_min:crop_y_max]

    if type(nuc_label) is np.ndarray:
        print('Nuclear Segmentations found...')
        tf = read_image(raw_image)
        mean_signal = {}
        for x_shift in range(-50, 50):
            mean_signal[x_shift] = {}
            for y_shift in range(-50,50):
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