import glob, os
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import time

from skimage.transform import rescale
import scipy.ndimage as ndimage
import imageio
import h5py

import matplotlib.pyplot as plt
import seaborn as sns
from skimage.io import imsave
from pyklb import readfull

x_sc = 0.208
y_sc = 0.208
z_sc = 2

def to_even(x):
    return 2*int(round(x/2))

def find_cropboxes(roots, indir, time_min = 50, time_max = 70, 
                   regime = 'h5',
                   which_cam = 'Long', plot = False, ws = 100, thres = 0.1):
    for root in roots:
        try:
            t0 = time.time()
            if regime == 'klb':
                images = glob.glob(root + '/out/folder_Cam_'+which_cam+'*/klbOut_Cam_'+which_cam+'*.klb') 
            elif regime == 'h5':
                images = glob.glob(root + '/Cam_'+which_cam+'*h5') 
            cur_name = root.split('/')[-1]
            print(cur_name)
            cur_dir = indir+cur_name
            vpairs = {}
            hpairs = {}
            num_boxes = {}
            all_ims = []
            for im in np.sort(images)[time_min:time_max]:
                cur_time = int(im.split('/')[-1].split('.')[0].split('_')[-1])
                #print(cur_time)
                if regime == 'h5':
                    a = h5py.File(im,'r')
                    a = a['Data'] 
                elif regime == 'klb':
                    #print(im)
                    a = readfull(str(im))
                corrected = a[:,:,:].astype('float64')-a[-1,:,:].astype('float64')
    #             if plot:
    #                 plt.figure()
    #                 plt.imshow(a[-1,:,:].astype('float64'))
    #                 plt.show()
    #                 plt.figure()
    #                 plt.imshow(a[0,:,:].astype('float64'))
    #                 plt.show()
                all_ims.append(corrected)
            all_ims = np.array(all_ims)
            corrected = all_ims.mean(0)
            sm1 = ndimage.uniform_filter(corrected.mean(1).mean(0), ws)
            sm2 = ndimage.uniform_filter(corrected.mean(2).mean(0), ws)
            if plot:
                plt.figure()
                plt.plot(sm2/max(sm2))
                plt.axhline(thres)
                plt.show()
            vboxes = (sm2/max(sm2)>thres).astype(int)
            vboxes = np.concatenate([[0], vboxes])
            vboxes = np.concatenate([vboxes, [0]])
            bndrs = np.where((vboxes[1:] - vboxes[:-1])!=0)[0]
                    #print(bndrs)
            if len(bndrs) % 2 != 0:
                print('something wrong')
                continue
            else:
                num_boxes['all'] = len(bndrs) // 2
            vpairs['all'] = [(to_even(bndrs[2*k]), to_even(bndrs[2*k+1])) for k in range(num_boxes['all'])]
            hpairs['all'] = []
            for pair in vpairs['all']:
                try:
                    sm = ndimage.uniform_filter(corrected.mean(0)[pair[0]:pair[1],:].mean(0), ws)       
                    if plot:
                        plt.figure()
                        plt.plot(sm/max(sm))
                        plt.axhline(thres)
                        plt.show()
                    hbox = (sm/max(sm)>thres).astype(int)
                    hbox = np.concatenate([[0], hbox])
                    hbox = np.concatenate([hbox, [0]])
                    bndrs = np.where((hbox[1:] - hbox[:-1])!=0)[0]
                    hpairs['all'].append((to_even(bndrs[0]), to_even(bndrs[1])))
                except:
                    vpairs['all'].pop(pair)

            num_boxes = pd.Series(num_boxes)
            vpairs = pd.DataFrame(vpairs)
            hpairs = pd.DataFrame(hpairs)
            print(vpairs, hpairs)
            vpairs.to_csv(cur_dir + '/cropped/cropboxes/vpairs.csv')
            hpairs.to_csv(cur_dir + '/cropped/cropboxes/hpairs.csv')
            t1 = time.time()
            print('Finished cropping in '+str(t1-t0)+ 'sec')
        except:
            print('Something went wrong')
            continue
        
def visualize_crops(roots, indir, regime = 'h5', 
                    timepoint = 50,
                    show = False, which_cam = 'Long'):
    num_rows = (len(roots) // 3) + 1
    plt.figure(figsize = (15, 5 * num_rows))
    i = 1
    for root in roots:
        plt.subplot(num_rows,3,i)
        i+=1
        cur_name = root.split('/')[-1]
        print(cur_name)
        cur_dir = indir+cur_name
        spl = indir.split('/')
        last = cur_name.split('_')
        memroot = '/'.join(spl[:-1])+'/'+'_'.join(last[:3])+'_0_obj_left/'
        #nucroot = '/'.join(spl[:-1])+'/'+'_'.join(last[:3])+'_2_obj_left/'
        try:
            vpairs = pd.read_csv(memroot + '/cropped/cropboxes/vpairs.csv', index_col = [0])
            hpairs = pd.read_csv(memroot + '/cropped/cropboxes/hpairs.csv', index_col = [0])
        except:
            continue
        vpairs = tuple(map(int, vpairs['all'][0][1:-1].split(', ')))
        hpairs = tuple(map(int, hpairs['all'][0][1:-1].split(', ')))
        crop_x_min = max(hpairs[0]-150,0)
        crop_x_max = min(hpairs[1]+150, 2048)
        crop_y_min = max(vpairs[0]-150,0)
        crop_y_max = min(vpairs[1]+150, 2048)
        if regime == 'klb':
            images = glob.glob(root + '/out/folder_Cam_'+which_cam+'*/klbOut_Cam_'+which_cam+'*.klb') 
        elif regime == 'h5':
            images = glob.glob(root + '/Cam_'+which_cam+'*h5') 
        im = np.sort(images)[timepoint]
        filename = im
        if regime == 'h5':
            a = h5py.File(im,'r')
            a = a['Data'] 
        elif regime == 'klb':
            #print(im)
            a = readfull(str(im))
        plt.imshow(np.array(a).max(0)[crop_y_min:crop_y_max, 
                                      crop_x_min:crop_x_max])
        plt.colorbar()
        plt.title('_'.join(last[:2]))
    plt.suptitle('Timepoint '+str(timepoint))
    plt.savefig(indir+'crops_tp_'+str(timepoint)+'.pdf')
    if show:
        plt.show()
    
def crop_membrane(roots, indir, regime = 'h5', which_cam = 'Long', offset = 150):
    for root in roots:
        t0 = time.time()
        cur_name = root.split('/')[-1]
        print(cur_name)
        cur_dir = indir+cur_name
        try:
            vpairs = pd.read_csv(cur_dir + '/cropped/cropboxes/vpairs.csv', index_col = [0])
            hpairs = pd.read_csv(cur_dir + '/cropped/cropboxes/hpairs.csv', index_col = [0])
        except:
            print('Cropboxes not found')
            continue
        if regime == 'klb':
            images = glob.glob(root + '/out/folder_Cam_'+which_cam+'*/klbOut_Cam_'+which_cam+'*.klb') 
        elif regime == 'h5':
            images = glob.glob(root + '/Cam_'+which_cam+'*h5') 
        vpairs = tuple(map(int, vpairs['all'][0][1:-1].split(', ')))
        hpairs = tuple(map(int, hpairs['all'][0][1:-1].split(', ')))
        v1 = max(hpairs[0]-offset,0)
        v2 = min(hpairs[1]+offset, 2048)
        h1 = max(vpairs[0]-offset,0)
        h2 = min(vpairs[1]+offset, 2048)
    #     if hpairs.index != vpairs.index:
    #         print('Something wrong with pair indices')
        for im in images:
            filename = im
            if regime == 'h5':
                a = h5py.File(im,'r')
                a = a['Data'] 
            elif regime == 'klb':
                #print(im)
                a = readfull(str(im))
            cur_num = filename.split('/')[-1].split('.')[0].split('_')[-1]
            cur_box = a[:, h1:h2, v1:v2]
            # rescale
            #cur_box_resc_low = zoom(cur_box, (1/(2*x_sc), 1/(2*z_sc), 1/(2*z_sc)))
            cur_box_resc_low = rescale(cur_box, 
                                       (1/(2*x_sc), 1/(2*z_sc), 1/(2*z_sc)), 
                                       preserve_range = True, 
                                       anti_aliasing = True)
            #cur_box_resc_high = zoom(cur_box, (z_sc/x_sc, 1, 1))

            #imsave(cur_dir+'/cropped/'+cur_num+'_box_'+str(box)+'.tif', cur_box, bigtiff=False)
            imsave(cur_dir+'/cropped/'+cur_num+'_rescaled_low.tif', cur_box_resc_low, bigtiff=False)
            #imsave(cur_dir+'/cropped/'+cur_num+'_box_'+str(box)+'_rescaled_high.tif', cur_box_resc_high, bigtiff=False)
        t1 = time.time()
        print('Finished cropping in '+str(t1-t0)+ 'sec')

#decided to separate one box (above) and multiple boxes (below) cases for safety

def crop_membrane_boxes(roots, indir, regime = 'h5', which_cam = 'Long', offset = 150):
    for root in roots:
        t0 = time.time()
        cur_name = root.split('/')[-1]
        print(cur_name)
        cur_dir = indir+cur_name
        try:
            vpairs_all = pd.read_csv(cur_dir + '/cropped/cropboxes/vpairs.csv', index_col = [0])
            hpairs_all = pd.read_csv(cur_dir + '/cropped/cropboxes/hpairs.csv', index_col = [0])
        except:
            print('Cropboxes not found')
            continue
        if regime == 'klb':
            images = glob.glob(root + '/out/folder_Cam_'+which_cam+'*/klbOut_Cam_'+which_cam+'*.klb') 
        elif regime == 'h5':
            images = glob.glob(root + '/Cam_'+which_cam+'*h5')
        for box in vpairs_all.index:
            print(box)
            print(vpairs_all['all'])
            print(hpairs_all['all'])
            vpairs = tuple(map(int, vpairs_all['all'][box][1:-1].split(', ')))
            hpairs = tuple(map(int, hpairs_all['all'][box][1:-1].split(', ')))
            v1 = max(hpairs[0]-offset,0)
            v2 = min(hpairs[1]+offset, 2048)
            h1 = max(vpairs[0]-offset,0)
            h2 = min(vpairs[1]+offset, 2048)
        #     if hpairs.index != vpairs.index:
        #         print('Something wrong with pair indices')
            for im in images:
                filename = im
                if regime == 'h5':
                    a = h5py.File(im,'r')
                    a = a['Data'] 
                elif regime == 'klb':
                    #print(im)
                    a = readfull(str(im))
                cur_num = filename.split('/')[-1].split('.')[0].split('_')[-1]
                cur_box = a[:, h1:h2, v1:v2]
                # rescale
                #cur_box_resc_low = zoom(cur_box, (1/(2*x_sc), 1/(2*z_sc), 1/(2*z_sc)))
                cur_box_resc_low = rescale(cur_box, 
                                           (1/(2*x_sc), 1/(2*z_sc), 1/(2*z_sc)), 
                                           preserve_range = True, 
                                           anti_aliasing = True)
                #cur_box_resc_high = zoom(cur_box, (z_sc/x_sc, 1, 1))

                #imsave(cur_dir+'/cropped/'+cur_num+'_box_'+str(box)+'.tif', cur_box, bigtiff=False)
                os.makedirs(cur_dir+'/cropped/box_'+str(box), exist_ok = True)
                imsave(cur_dir+'/cropped/box_'+str(box)+'/'+cur_num+'_rescaled_low.tif', cur_box_resc_low, bigtiff=False)
                #imsave(cur_dir+'/cropped/'+cur_num+'_box_'+str(box)+'_rescaled_high.tif', cur_box_resc_high, bigtiff=False)
        t1 = time.time()
        print('Finished cropping in '+str(t1-t0)+ 'sec')

