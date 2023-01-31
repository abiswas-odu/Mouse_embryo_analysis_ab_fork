#!/bin/bash

#SBATCH --job-name=erode_labels  # create a short name for your job
#SBATCH --nodes=1                # node count
#SBATCH --ntasks=1               # total number of tasks across all nodes
#SBATCH --mem=40G                # total memory per node
#SBATCH --time=12:00:00          # total run time limit (HH:MM:SS)
#SBATCH -A molbio


IMAGE_PATH="/tigress/LIGHTSHEET/posfailab/ab50/tools/Mouse_embryo_analysis_ab_fork/test/image_data"
NUCL_SEG_DIR="/tigress/LIGHTSHEET/posfailab/ab50/tools/Mouse_embryo_analysis_ab_fork/test/nucl_seg"
OUT_DIR="/tigress/LIGHTSHEET/posfailab/ab50/tools/Mouse_embryo_analysis_ab_fork/test/output"

##===================================================================================================
##=====================CHANGES BELOW THIS LINE FOR ADVANCED USERS====================================
##===================================================================================================

footprint_size="3"
generate_contour="--gen_contour"

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

python ${SCRIPT_PATH}/tf_extract.py erode-labels \
  --orig_image_dir ${IMAGE_PATH} \
  --nucl_seg_dir ${NUCL_SEG_DIR} \
  --out_dir ${OUT_DIR} \
  --footprint_size ${footprint_size} \
  ${generate_contour}

echo Ending time is $(date)
endtime=$(date +"%s")
diff=$(($endtime - $starttime))
echo Elapsed time is $(($diff/60)) minutes and $(($diff%60)) seconds.

