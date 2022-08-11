import numpy as np
import pandas as pd
import seaborn as sns
import glob
from skimage import io
import matplotlib.pyplot as plt
import os

def read_segments(cur_stack, membrane, nuclear, out):
    nuc_labels= {}               
    mem_labels = {}
    #nuclei
    try:
        root = nuclear
        images = glob.glob(root+'*.tif')  
        nuc_labels = {}
        for im in np.sort(images):
            cur_name = im.split('/')[-1]
            time = cur_name.split('_')[3].split('.')[0]
            #print(time)
            nuc_labels[int(time)] = io.imread(im)
    except:
        try:
            root = nuclear
            images = glob.glob(root+'*.tif')  
            nuc_labels = {}
            for im in np.sort(images):
                cur_name = im.split('/')[-1]
                time = cur_name.split('_')[4].split('.')[0]
                #print(time)
                nuc_labels[int(time)] = io.imread(im)
        except:
            print('Problem with reading nuclear segments')
            pass
        
    #membrane 
    try:
        root = membrane
        images = glob.glob(root+'*_cp_masks.tif')  
        mem_labels = {}
        for im in np.sort(images):
            cur_name = im.split('/')[-1]
            time = cur_name.split('_')[0]
            #print(time)
            mem_labels[int(time)] = io.imread(im)
    except:
        print('Problem with reading membrane segments')
        pass
    return mem_labels, nuc_labels

