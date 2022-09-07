from io_utils import read_image
import os

# Reads segmentation results for both membrane and nuclei

# Parameters:
# # membrane_file  = file with membrane segmentation results
# # nuclear_file  = file with nuclear segmentation results
# # nuclear_file_cirrected  = file with hand corrected nuclear segmentation results
# Returns:
# # mem_mask = membrane labels indexed
# # nuc_mask = nuclear labels indexed
# Will return None if one or both the segmentation types is unavailable

def read_segments(data_dir, file_prefix, file_ext, segmentation_type):
    # Initialize masks to None
    label_mask = None
    # nuclei
    try:
        if segmentation_type == "membrane":
            mem_file = os.path.join(data_dir, file_prefix + "_cp_masks" + file_ext)
            if os.path.exists(mem_file):
                label_mask = read_image(mem_file)
            else: # Check the other cam
                if 'Long' in file_prefix:
                    replace_cam_prefix = file_prefix.replace('Long','Short')
                else:
                    replace_cam_prefix = file_prefix.replace('Short','Long')
                mem_file = os.path.join(data_dir, replace_cam_prefix + "_cp_masks" + file_ext)
                if os.path.exists(mem_file):
                    label_mask = read_image(mem_file)
        else:
            nucl_segm_file = os.path.join(data_dir,file_prefix + ".label" + file_ext)
            nucl_segm_file_corrected = os.path.join(data_dir,file_prefix + "_SegmentationCorrected" + file_ext)
            if os.path.exists(nucl_segm_file_corrected): # Look for corrected mask first
                label_mask = read_image(nucl_segm_file_corrected)
            elif os.path.exists(nucl_segm_file):
                label_mask = read_image(nucl_segm_file)
            else: # Check the other Cam
                if 'Long' in file_prefix:
                    replace_cam_prefix = file_prefix.replace('Long','Short')
                else:
                    replace_cam_prefix = file_prefix.replace('Short','Long')
                nucl_segm_file = os.path.join(data_dir,replace_cam_prefix + ".label" + file_ext)
                nucl_segm_file_corrected = os.path.join(data_dir,replace_cam_prefix + "_SegmentationCorrected" + file_ext)
                if os.path.exists(nucl_segm_file_corrected): # Look for corrected mask first
                    label_mask = read_image(nucl_segm_file_corrected)
                elif os.path.exists(nucl_segm_file):
                    label_mask = read_image(nucl_segm_file)
    except Exception as e:
            print('Problem with reading segments', e)

    return label_mask
