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

def quantify_tf(root, indir, cur_stack, nuc_labels, mem_labels, cell_volume_cutoff = 0, max_time = 120, offset = 150, max_margin = 2048, which_cam = 'Short', regime = 'klb', x_shift = 0, y_shift = 0):
    #cur_name = root.split('/')[-1]
    #cur_dir = indir+cur_name
    vpairs = pd.read_csv(indir + cur_stack+'_channel_0_obj_left/cropped/cropboxes/vpairs.csv', index_col = [0])
    hpairs = pd.read_csv(indir + cur_stack+'_channel_0_obj_left/cropped/cropboxes/hpairs.csv', index_col = [0]) 
    vpairs = tuple(map(int, vpairs['all'][0][1:-1].split(', ')))
    hpairs = tuple(map(int, hpairs['all'][0][1:-1].split(', ')))
    crop_y_min = max(hpairs[0]+y_shift-offset,0)
    crop_y_max = min(hpairs[1]+y_shift+offset, max_margin)
    crop_x_min = max(vpairs[0]+x_shift-offset,0)
    crop_x_max = min(vpairs[1]+x_shift+offset, max_margin)
    # Nuclear crop

    sns.set(font_scale = 2, style = 'white')
    cdx = {}
    #for root in roots:
    if regime == 'h5':
        cdx_dat = glob.glob(root + '/Cam_'+which_cam+'*h5')
    else:
        cdx_dat = glob.glob(root+'/out/folder_Cam_Long*/klbOut_Cam_Long*.klb')
    #print(cdx_dat)
    #cur_stack = root.split('/')[-1].split('_')[1]
    cdx[cur_stack] = {}

    #images = glob.glob(cur_dir + '/cropped_masks/new/*box_'+str(box)+'*6p25*')  
    #num_labels = {}
    nuc_cdx_vals = {}
    mem_cdx_vals = {}
    for i, im in enumerate(np.sort(cdx_dat)):
        try:
            if regime == 'h5':
                a = h5py.File(im,'r')
                a = a['Data'][:, crop_x_min:crop_x_max, crop_y_min:crop_y_max] 
            else:
                a = readfull(str(im))#h5py.File(im,'r')
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
                nuc_cdx_vals[int(cur_num)] = {}
                mem_cdx_vals[int(cur_num)] = {}
                for lab in np.unique(nuc_mask):
                    nuc_cdx_vals[int(cur_num)][lab] = np.mean(a[nuc_mask == lab])
                for lab in np.unique(mem_mask):
                    if np.sum(mem_mask == lab)>=cell_volume_cutoff:
                        mem_cdx_vals[int(cur_num)][lab] = np.mean(a_mem[mem_mask == lab])
        except:
            continue

    return mem_cdx_vals, nuc_cdx_vals

def quantify_tf_couplets(root, indir, cur_stack, cur_box, nuc_labels, mem_labels, max_time = 120, offset = 150, max_margin = 2048, which_cam = 'Short'):
    #cur_name = root.split('/')[-1]
    #cur_dir = indir+cur_name
    vpairs = pd.read_csv(indir + cur_stack+'_'+cur_box+'_channel_0_obj_left/cropped/cropboxes/vpairs.csv', index_col = [0])
    hpairs = pd.read_csv(indir + cur_stack+'_'+cur_box+'_channel_0_obj_left/cropped/cropboxes/hpairs.csv', index_col = [0]) 
    vpairs = tuple(map(int, vpairs['all'][0][1:-1].split(', ')))
    hpairs = tuple(map(int, hpairs['all'][0][1:-1].split(', ')))
    crop_y_min = max(hpairs[0]-offset,0)
    crop_y_max = min(hpairs[1]+offset, max_margin)
    crop_x_min = max(vpairs[0]-offset,0)
    crop_x_max = min(vpairs[1]+offset, max_margin)
    # Nuclear crop

    sns.set(font_scale = 2, style = 'white')
    cdx = {}
    #for root in roots:
    #cdx_dat = glob.glob(root + '/Cam_'+which_cam+'*h5')
    cdx_dat = glob.glob(root+'/out/folder_Cam_Long*/klbOut_Cam_Long*.klb')
    #print(cdx_dat)
    #cur_stack = root.split('/')[-1].split('_')[1]
    cdx[cur_stack] = {}

    #images = glob.glob(cur_dir + '/cropped_masks/new/*box_'+str(box)+'*6p25*')  
    #num_labels = {}
    nuc_cdx_vals = {}
    mem_cdx_vals = {}
    for i, im in enumerate(np.sort(cdx_dat)):
        try:
            a = readfull(str(im))#h5py.File(im,'r')
            #a = a['Data'][:, crop_x_min:crop_x_max, crop_y_min:crop_y_max]           
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
                nuc_cdx_vals[int(cur_num)] = {}
                mem_cdx_vals[int(cur_num)] = {}
                for lab in np.unique(nuc_mask):
                    nuc_cdx_vals[int(cur_num)][lab] = np.mean(a[nuc_mask == lab])
                for lab in np.unique(mem_mask):
                    mem_cdx_vals[int(cur_num)][lab] = np.mean(a_mem[mem_mask == lab])
        except:
            continue

    return mem_cdx_vals, nuc_cdx_vals
