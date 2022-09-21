def map_nuclei_to_cells(embryos, indir, outdir, volume_cutoff = 3000)
    for i in embryos:#range(num_embryos):
        cur_stack = 'stack_'+str(i)
        print(cur_stack)
        membrane, nuclear, out = mydirs(indir, cur_stack, outdir = outdir) 
        good_nuc_labels[cur_stack] = pd.read_csv(indir+cur_stack+'_channel_0_obj_left/good_nuc_labels.csv')
        good_nuc_labels[cur_stack] = good_nuc_labels[cur_stack].to_dict()
        try:
            cor_cel = pd.read_csv(out + 'analysis/nuclei_map_to_cells_IoU.csv', index_col = [0])
        except:
            print('Looking for correspondences...')
            #mem_labels, nuc_labels = read_segments(cur_stack, membrane, nuclear, out)        
            #if not os.path.exists(out + 'analysis/cells_map_to_nuclei_IoU.csv'):
            corr_cell = {}
            iou = {}
            for time in list(nuc_labels.keys()):
                if int(time)>0 and int(time)<max_time:
                    print(time)
                    corr_cell[time] = {}
                    iou[time] = {}
                    ml = mem_labels[time]
                    nl = nuc_labels[time]
                    for nuclab in good_nuc_labels[cur_stack][time]:
                        inters = {}
                        ious = {}
                        mem_wh = np.where((nl==nuclab))
                        resc_wh = []
                        rr = (mem_wh[0]/56*135).astype(int)
                        resc_wh.append(np.concatenate([rr-1, rr, rr+1]))
                        rr = (mem_wh[1]/4).astype(int)
                        resc_wh.append(np.concatenate([rr, rr, rr]))
                        rr = (mem_wh[2]/4).astype(int)
                        resc_wh.append(np.concatenate([rr, rr, rr]))
                        tf_array = np.zeros(ml.shape).astype(bool)
                        tf_array[tuple(resc_wh)] = True
                        for lab in set(np.unique(ml))-{0}:
                            if np.sum(ml == lab)<volume_cutoff:
                                continue
                            
                            inters[lab] = np.sum((ml == lab)*tf_array)#*(zoomback==memlab))
                            ious[lab] = inters[lab]/np.sum((ml == lab) | tf_array)
                        inters = pd.Series(inters)
                        if max(inters.values)>0:
                            cur_lab = pd.Series(inters).idxmax()
                            if cur_lab in iou[time].keys():
                                if ious[cur_lab]> iou[time][cur_lab]:
                                    key_to_remove = [k for k in corr_cell[time].keys() if corr_cell[time][k] == cur_lab][0]
                                    corr_cell[time].pop(key_to_remove)
                                    corr_cell[time][nuclab] = cur_lab
                                    iou[time][cur_lab] = ious[cur_lab]   
                            else:
                                iou[time][cur_lab] = ious[cur_lab]               
                                corr_cell[time][nuclab] = cur_lab
                    corr_cell[time][0]=0
            cor_cel = pd.DataFrame(corr_cell)
            cor_cel = cor_cel.loc[(~(pd.isnull(cor_cel))).sum(1)>0,:]
            cor_cel = cor_cel.loc[(cor_cel!=0).sum(1)>0,:]
            cor_cel.columns.names = ['Time']
            cor_cel.index.names = ['Nuclear_Label']
            cor_cel.to_csv(out + 'analysis/nuclei_map_to_cells_IoU.csv')