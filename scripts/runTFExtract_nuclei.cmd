#!/bin/bash

#SBATCH --job-name=extract_TF    # create a short name for your job
#SBATCH --nodes=1                # node count
#SBATCH --ntasks=1               # total number of tasks across all nodes
#SBATCH --mem=40G                # total memory per node
#SBATCH --time=12:00:00          # total run time limit (HH:MM:SS)
#SBATCH -A molbio


NUCL_IMAGE_DIR="/tigress/LIGHTSHEET/posfailab/ab50/tools/Mouse_embryo_analysis_ab_fork/test/extract_test/nuclei_images"
TF_IMAGE_DIR="/tigress/LIGHTSHEET/posfailab/ab50/tools/Mouse_embryo_analysis_ab_fork/test/extract_test/nuclei_images"
NUCL_SEG_DIR="/tigress/LIGHTSHEET/posfailab/ab50/tools/Mouse_embryo_analysis_ab_fork/test/extract_test/nucl_seg"
CROP_DIR="/tigress/LIGHTSHEET/posfailab/ab50/tools/Mouse_embryo_analysis_ab_fork/test/extract_test/crop"
OUTPUT_FILE_NAME=""
timestamp_min="0"
timestamp_max="10"

##===================================================================================================
##=====================CHANGES BELOW THIS LINE FOR ADVANCED USERS====================================
##===================================================================================================

crop_index="0"
offset="150"
cell_volume_cutoff="2000"
image_size=2048

## Change to 0, to not align camera automatically and use override. 
## If set to 1, the overrides are ignored 
align_camera="1" 
x_shift_override="24"
y_shift_override="23"

##===================================================================================================
##==============================NO CHANGES BELOW THIS LINE===========================================
##===================================================================================================

echo Running on host `hostname`
echo Starting Time is `date`
echo Directory is `pwd`
starttime=$(date +"%s")

module purge
module load anaconda3/2020.11
export LD_LIBRARY_PATH=/projects/LIGHTSHEET/posfailab/ab50/tools/keller-lab-block-filetype/build/src
conda activate /projects/LIGHTSHEET/posfailab/ab50/tools/tf2-posfai

SCRIPT_PATH=/tigress/LIGHTSHEET/posfailab/ab50/tools/Mouse_embryo_analysis_ab_fork

python ${SCRIPT_PATH}/tf_extract.py tf-align-simple \
  --nucl_image_dir ${NUCL_IMAGE_DIR} \
  --tf_signal_image_dir ${TF_IMAGE_DIR} \
  --nucl_seg_dir ${NUCL_SEG_DIR} \
  --crop_dir ${CROP_DIR} \
  --cropbox_index ${crop_index} \
  --timestamp_min ${timestamp_min} \
  --timestamp_max ${timestamp_max} \
  --offset ${offset} \
  --cell_volume_cutoff ${cell_volume_cutoff} \
  --max_margin ${image_size} \
  --align_camera ${align_camera} \
  --x_shift_override ${x_shift_override} \
  --y_shift_override ${y_shift_override}

echo Ending time is $(date)
endtime=$(date +"%s")
diff=$(($endtime - $starttime))
echo Elapsed time is $(($diff/60)) minutes and $(($diff%60)) seconds.

