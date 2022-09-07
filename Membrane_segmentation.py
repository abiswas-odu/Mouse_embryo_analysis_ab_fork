import os, glob
import pandas as pd
import numpy as np
import copy

import matplotlib.pyplot as plt

import scipy.ndimage as ndimage
import skimage.feature as feature
import skimage.morphology as morphology
import skimage.measure as measure
import skimage.filters as filters

from skimage.filters import sobel
from skimage.morphology import disk, ball
from skimage.util import img_as_uint

from skimage.segmentation import watershed
from skimage import io
from skimage.io import imsave
import scipy
from skimage import restoration
from skimage.filters import gaussian
from skimage.feature import peak_local_max

def segment_membrane(indir, time_limit = '7-0'):
    os.makedirs(indir+'/logs/', exist_ok = True)
    os.makedirs(indir+'/results/', exist_ok = True)
    roots = glob.glob(indir+'*channel_0*')
    #outdir = '/mnt/home/mavdeeva/ceph/mouse/maddy_data/segmentation_out/210809/'
    for root in roots:
        cur_name = root.split('/')[-1]
        print(cur_name)
        #cur_dir = outdir+cur_name
        spl = root.split('/')
        last = spl[-1].split('_')
        stack_name = '_'.join(last[:2])
        sub = open(indir+'/submission_'+stack_name+'.sh', "w")
        sub.write('#!/bin/bash \n')
        sub.write('srun python3 -m cellpose --dir ' + root +'/cropped --pretrained_model cyto2 --chan 0 --save_tif --check_mk --do_3D --use_gpu --no_npy')
        sub.close()
        #sbatch -p ccb -n 1 --ntasks-per-node 3 
        #sbatch --partition gpu --gpus 1 -c 1 --constraint=v100-32gb
        #module load gcc python3 cuda/11.4.2 cudnn/8.2.4.15-11.4 slurm
        os.system('sbatch --partition gpu --gpus 1 -c 1 --constraint=v100-32gb -t '+str(time_limit)+'  '+indir+'/submission_'+stack_name+'.sh')
        
def segment_membrane_boxes(indir, time_limit = '7-0'):
    os.makedirs(indir+'/logs/', exist_ok = True)
    os.makedirs(indir+'/results/', exist_ok = True)
    roots = glob.glob(indir+'*channel_0*')
    #outdir = '/mnt/home/mavdeeva/ceph/mouse/maddy_data/segmentation_out/210809/'
    for root in roots:
        boxroots = glob.glob(root +'/cropped/box*')
        for boxroot in boxroots: 
            cur_box = boxroot.split('/')[-1]
            cur_name = root.split('/')[-1]
            print(cur_name)
            #cur_dir = outdir+cur_name
            spl = root.split('/')
            last = spl[-1].split('_')
            stack_name = '_'.join(last[:2])
            sub = open(indir+'/submission_'+stack_name+'_'+cur_box+'.sh', "w")
            sub.write('#!/bin/bash \n')
            sub.write('srun python3 -m cellpose --dir ' + boxroot +' --pretrained_model cyto2 --chan 0 --save_tif --check_mk --do_3D --use_gpu --no_npy')
            sub.close()
            #sbatch -p ccb -n 1 --ntasks-per-node 3 
            #sbatch --partition gpu --gpus 1 -c 1 --constraint=v100-32gb
            #module load gcc python3 cuda/11.4.2 cudnn/8.2.4.15-11.4 slurm
            os.system('sbatch --partition gpu --gpus 1 -c 1 --constraint=v100-32gb -t '+str(time_limit)+'  '+indir+'/submission_'+stack_name+'_'+cur_box+'.sh')
            
def segment_couplet_membranes(root, plot = False, only_final_plot = False, ss = 40,
                              gaussian_sigma = 2, niblack_rad = 31, closing_rad = 3,
                              logb_cutoff = 4.7, 
                              label_min_volume_cutoff = 1000, 
                              label_max_volume_cutoff = 100000, 
                              make_gifs = False, with_time = True):
    #print('hi')
    from skimage.filters import threshold_otsu, scharr
    #from skimage.feature import canny
    boxroots = glob.glob(root +'/cropped/box*')
    for boxroot in boxroots: 
        cur_box = boxroot.split('/')[-1]
        cur_name = root.split('/')[-1]
        print(cur_name)
        #cur_dir = outdir+cur_name
        spl = root.split('/')
        last = spl[-1].split('_')
        stack_name = '_'.join(last[:2])
        images = np.sort(glob.glob(boxroot +'/*rescaled_low.tif'))
        for im in images:
            cur_name = im.split('/')[-1]
            #print(cur_name)
            b = io.imread(im)
            b_blur = gaussian(b, sigma = gaussian_sigma, multichannel = False)
            #selem = ball(4)
            img0 = scharr(b_blur)
            img = gaussian(sobel(b_blur), sigma = gaussian_sigma, multichannel = False)
            img2 = img_as_uint(img/np.max(img))
            img0_2 = img_as_uint(img0/np.max(img0))
            rad = closing_rad
            kernel = np.ones((rad, rad, rad)).astype("uint8")
            #selem = ball(radius)
            local_thres = filters.threshold_niblack(img2, window_size = niblack_rad)
            logb_cutoff = threshold_otsu(np.log(b_blur))-0.02
            res0 = (img2>local_thres-200)
            res00 = (np.log(b_blur)>logb_cutoff)
            res = (img2>local_thres-200)*(np.log(b_blur)>logb_cutoff)

            res1 = morphology.closing(res, selem = kernel)#morphology.binary_closing(morphology.binary_opening(res), ball(3))
            labels = measure.label(1.-res1)

            #print('labeled')
            y = np.bincount(np.ravel(labels))
            #print(y)
            labels_to_remove = np.where(y>label_max_volume_cutoff)[0]
            #print(labels_to_remove)
            #labels = np.array([0 if x in labels_to_remove else x for x in np.ravel(labels)]).reshape(labels.shape)
            for k in labels_to_remove: 
                if k!=0:
                    labels[labels==k] = 1
            labels_to_remove = np.where(y<label_min_volume_cutoff)[0]
            #print(labels_to_remove)
            #labels = np.array([0 if x in labels_to_remove else x for x in np.ravel(labels)]).reshape(labels.shape)
            for k in labels_to_remove: 
                if k!=0:
                    labels[labels==k] = 0
            #print('start watershed')
            labels_w = watershed(img0_2, markers = labels)


            #reorder by size
            y = np.bincount(np.ravel(labels_w))
            #print(y)
            reordered = copy.deepcopy(labels_w)
            if len(y)>2:
                order = np.argsort(y[2:])[::-1]
                #print(order)
                for i,k in enumerate(order):
                    reordered[labels_w == 2+k] = 2+i
            reordered = reordered-1
            y = np.bincount(np.ravel(reordered))
            labels_to_remove = np.where(y>label_max_volume_cutoff)[0]
            for k in labels_to_remove: 
                if k!=0:
                    reordered[reordered==k] = 0
                    
            #diameters
            try:
                data_slices = ndimage.find_objects(reordered)
                sizes = np.array([[s.stop-s.start for s in object_slice] 
                          for object_slice in data_slices])
                print(sizes)
                labels_to_remove = np.where(sizes.max(1)>100)[0]
                for k in labels_to_remove: 
                    reordered[reordered==(k+1)] = 0
            except:
                continue

            #print(np.bincount(np.ravel(reordered)))
            if plot:
                if only_final_plot:
                    plt.figure(figsize = (5,5))
                    plt.imshow(reordered[ss,:,:])
                    plt.show()
                else:
                    plt.figure(figsize = (20,10))
                    plt.subplot(2,4,1)
                    plt.imshow(b_blur[ss,:,:])
                    plt.subplot(2,4,2)
                    plt.imshow(img2[ss,:,:])
                    plt.subplot(2,4,3)
                    plt.imshow(res0[ss,:,:])
                    plt.subplot(2,4,4)
                    plt.imshow(res00[ss,:,:])
                    plt.subplot(2,4,5)
                    plt.imshow(res[ss,:,:])
                    plt.subplot(2,4,6)
                    plt.imshow(res1[ss,:,:])
                    plt.subplot(2,4,7)
                    plt.imshow(labels[ss,:,:])
                    plt.subplot(2,4,8)
                    plt.imshow(reordered[ss,:,:])
                    plt.show()
            imsave(boxroot+'/'+cur_name.split('.')[0]+'_cp_masks.tif', reordered.astype('float'), bigtiff=False)
            
def segment_couplets_all(indir, time_limit = '7-0'):
    roots = glob.glob(indir+'*channel_0*')
    for root in np.sort(roots):
        spl = root.split('/')
        last = spl[-1].split('_')
        stack_name = '_'.join(last[:2])
        os.system('sbatch -p ccb -n 1 --ntasks-per-node 3 '+indir+'submission_'+stack_name+'.sh')