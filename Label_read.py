import numpy as np
import pandas as pd
import seaborn as sns
import glob
from skimage import io
import matplotlib.pyplot as plt
import os

from pyklb import readfull

# Reads segmentation results for both membrane and nuclei

# Parameters:
# # membrane = directory with membrane segmentation results
# # nuclear = directory with nuclear segmentation results

# Assumes one image file per timepoint in each directory

# Returns:
# # mem_labels = dictionary of membrane labels indexed by timepoint
# # nuc_labels = dictionary of nuclear labels indexed by timepoint

# Will return an empty dictionary if one of the segmentation types is unavailable

def read_segments(membrane, nuclear):
    nuc_labels= {}               
    mem_labels = {}
    #nuclei
    try:
        root = nuclear
        images = glob.glob(nuclear+'*.klb')  
        nuc_labels = {}
        for im in np.sort(images):
            cur_name = im.split('/')[-1]
            time = int(cur_name.split('.')[0].split('_')[-1])
            #print(time)
            nuc_labels[time] = readfull(str(im))
    except:
            print('Problem with reading nuclear segments')
            pass        
    #membrane 
    try:
        root = membrane
        images = glob.glob(membrane+'*_cp_masks.tif')  
        mem_labels = {}
        for im in np.sort(images):
            cur_name = im.split('/')[-1]
            time = int(cur_name.split('_')[0])
            #print(time)
            mem_labels[time] = io.imread(im)
    except:
        print('Problem with reading membrane segments')
        pass
    return mem_labels, nuc_labels
