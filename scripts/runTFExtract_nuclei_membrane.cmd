#!/bin/bash

#SBATCH --job-name=extract_TF    # create a short name for your job
#SBATCH --nodes=1                # node count
#SBATCH --ntasks=1               # total number of tasks across all nodes
#SBATCH --mem=40G                # total memory per node
#SBATCH --time=12:00:00          # total run time limit (HH:MM:SS)
#SBATCH -A molbio


NUCL_IMAGE_DIR="/projects/LIGHTSHEET/posfailab/ab50/tools/Mouse_embryo_analysis_ab_fork/test/extract_test/nuclei_images"
TF_IMAGE_DIR="/tigress/LIGHTSHEET/posfailab/ab50/tools/Mouse_embryo_analysis_ab_fork/test/extract_test/nuclei_images"
MEMBRANE_IMAGE_DIR="/projects/LIGHTSHEET/posfailab/ab50/tools/Mouse_embryo_analysis_ab_fork/test/extract_test/membrane_images"
NUCL_SEG_DIR="/projects/LIGHTSHEET/posfailab/ab50/tools/Mouse_embryo_analysis_ab_fork/test/extract_test/nucl_seg"
MEMBRANE_SEG_DIR="/projects/LIGHTSHEET/posfailab/ab50/tools/Mouse_embryo_analysis_ab_fork/test/extract_test/mem_seg"
CROP_DIR="/projects/LIGHTSHEET/posfailab/ab50/tools/Mouse_embryo_analysis_ab_fork/test/extract_test/crop"
OUT_DIR="/tigress/LIGHTSHEET/posfailab/ab50/tools/Mouse_embryo_analysis_ab_fork/test/extract_test/output"
OUTPUT_FILE_PREFIX="test"
timestamp_min="0"
timestamp_max="10"

##===================================================================================================
##=====================CHANGES BELOW THIS LINE FOR ADVANCED USERS====================================
##===================================================================================================

crop_index="0"
offset="150"
cell_volume_cutoff="2000"
image_size="2048"
rescale="True"

## Change to 0, to not align camera automatically and use override.
## If set to 1, the overrides are ignored
align_camera="1"
align_cam_timestamps="0,4,9" # Pass an empty string "" if you want to use the first, mid and last
max_abs_shift="10"           # The absolute value of MAX shift to be explored in X and Y for camera alignment.
                             # Make ths small for faster alignment.

x_shift_override="24"        # Override for X shift if align_camera="0"
y_shift_override="23"        # Override for X shift if align_camera="1"

# Set option to toggle background extraction
extract_background="1"

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

## Loading directories to scratch
SCARCH_RUN_DIR=/scratch/gpfs/${USER}/${SLURM_JOB_ID}
mkdir ${SCARCH_RUN_DIR}
mkdir ${SCARCH_RUN_DIR}/NUCL_IMAGE
rsync -rL ${NUCL_IMAGE_DIR}/ ${SCARCH_RUN_DIR}/NUCL_IMAGE
mkdir ${SCARCH_RUN_DIR}/TF_IMAGE
rsync -rL ${TF_IMAGE_DIR}/ ${SCARCH_RUN_DIR}/TF_IMAGE
mkdir ${SCARCH_RUN_DIR}/MEMBRANE_IMAGE
rsync -rL ${MEMBRANE_IMAGE_DIR}/ ${SCARCH_RUN_DIR}/MEMBRANE_IMAGE
mkdir ${SCARCH_RUN_DIR}/MEMBRANE_SEG
rsync -rL ${MEMBRANE_SEG_DIR}/ ${SCARCH_RUN_DIR}/MEMBRANE_SEG
mkdir ${SCARCH_RUN_DIR}/NUCL_SEG
rsync -rL ${NUCL_SEG_DIR}/ ${SCARCH_RUN_DIR}/NUCL_SEG
mkdir ${SCARCH_RUN_DIR}/CROP
[[ -n "$CROP_DIR" ]] && rsync -rL ${CROP_DIR}/ ${SCARCH_RUN_DIR}/CROP
mkdir ${SCARCH_RUN_DIR}/OUT

# Run the command off scratch
SCRIPT_PATH=/tigress/LIGHTSHEET/posfailab/ab50/tools/Mouse_embryo_analysis_ab_fork
align_timestamp_params=$([[ -n "$align_cam_timestamps" ]] && echo "--align_camera_timestamps ${align_cam_timestamps}")
python ${SCRIPT_PATH}/tf_extract.py tf-align-simple \
  --nucl_image_dir ${SCARCH_RUN_DIR}/NUCL_IMAGE \
  --tf_signal_image_dir ${SCARCH_RUN_DIR}/TF_IMAGE \
  --nucl_seg_dir ${SCARCH_RUN_DIR}/NUCL_SEG \
  --membrane_image_dir ${SCARCH_RUN_DIR}/MEMBRANE_IMAGE \
  --membrane_seg_dir ${SCARCH_RUN_DIR}/MEMBRANE_SEG \
  --crop_dir ${SCARCH_RUN_DIR}/CROP \
  --out_dir ${OUT_DIR} \
  --out_prefix ${OUTPUT_FILE_PREFIX} \
  --cropbox_index ${crop_index} \
  --timestamp_min ${timestamp_min} \
  --timestamp_max ${timestamp_max} \
  --rescale ${rescale} \
  --offset ${offset} \
  --cell_volume_cutoff ${cell_volume_cutoff} \
  --max_margin ${image_size} \
  --align_camera ${align_camera} \
  ${align_timestamp_params} \
  --max_absolute_shift ${max_abs_shift} \
  --x_shift_override ${x_shift_override} \
  --y_shift_override ${y_shift_override} \
  --extract_background ${extract_background}

# Copy output and remove files from scratch
rsync -r ${SCARCH_RUN_DIR}/OUT/ ${OUT_DIR}
rm -rf $SCARCH_RUN_DIR

echo Ending time is $(date)
endtime=$(date +"%s")
diff=$(($endtime - $starttime))
echo Elapsed time is $(($diff/60)) minutes and $(($diff%60)) seconds.

