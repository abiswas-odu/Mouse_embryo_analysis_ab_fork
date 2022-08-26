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

def read_segments(mem_segm_file, nucl_segm_file, nucl_segm_file_corrected):
    # Initialize masks to None
    nucl_mask = None
    memb_mask = None

    # nuclei
    try:
        if os.path.exists(nucl_segm_file_corrected): # Look for corrected mask first
            nucl_mask = read_image(nucl_segm_file_corrected)
        elif os.path.exists(nucl_segm_file):
            nucl_mask = read_image(nucl_segm_file)
    except Exception as e:
            print('Problem with reading nuclear segments', e)

    #membrane 
    try:
        if os.path.exists(mem_segm_file):
            memb_mask = read_image(mem_segm_file)
    except Exception as e:
        print('Problem with reading membrane segments', e)

    return memb_mask, nucl_mask
