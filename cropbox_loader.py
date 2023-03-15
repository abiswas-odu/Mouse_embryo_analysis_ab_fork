import os
import pandas as pd


def load_cropboxes(crop_dir: str, crop_box_index: int, offset: int, max_margin: int, max_abs_alignment_shift: int):

    # Check if corpboxes are present
    if crop_dir is not None and os.path.exists(crop_dir):
        vpairs_file = os.path.join(crop_dir,'vpairs.csv')
        hpairs_file = os.path.join(crop_dir,'hpairs.csv')
    else:
        vpairs_file = ''
        hpairs_file = ''
    if os.path.exists(vpairs_file) and os.path.exists(hpairs_file):
        print('Cropboxes found...')
        vpairs = pd.read_csv(vpairs_file, index_col = [0])
        hpairs = pd.read_csv(hpairs_file, index_col = [0])
        vpairs = tuple(map(int, vpairs['all'][crop_box_index][1:-1].split(', ')))
        hpairs = tuple(map(int, hpairs['all'][crop_box_index][1:-1].split(', ')))
        crop_y_min = max(hpairs[0]-offset,0)
        crop_y_max = min(hpairs[1]+offset, max_margin)
        crop_x_min = max(vpairs[0]-offset,0)
        crop_x_max = min(vpairs[1]+offset, max_margin)
    else: # If no cropboxes, trim out border shift space
        print('Cropboxes not found found. Using full image with border trim of:' + str(max_abs_alignment_shift) + 'px')
        crop_y_min = max_abs_alignment_shift
        crop_y_max = max_margin - max_abs_alignment_shift
        crop_x_min = max_abs_alignment_shift
        crop_x_max = max_margin - max_abs_alignment_shift
    return crop_y_min, crop_y_max, crop_x_min, crop_x_max