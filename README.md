# Mouse_embryo_analysis

## Extracting transcription factor signal on Della

Executing the TF extraction program is best done using the scripts named ``runTFExtract_xxx.cmd`` in the scripts directory.

## Eroding labels to better fit the nuclei on Della

Executing the Erosion program is best done using the script ``runGenErodedLabels.cmd`` in the scripts directory.

## View help on Della
```commandline
module purge
module load anaconda3/2020.11
export LD_LIBRARY_PATH=/projects/LIGHTSHEET/posfailab/ab50/tools/keller-lab-block-filetype/build/src
conda activate /projects/LIGHTSHEET/posfailab/ab50/tools/tf2-posfai
python /tigress/LIGHTSHEET/posfailab/ab50/tools/Mouse_embryo_analysis_ab_fork tf_extract.py --help
```

## Installing on your own laptop

Download the package
```commandline
git pull https://github.com/abiswas-odu/Mouse_embryo_analysis_ab_fork.git@princeton_release
```
Load the `segmentation` conda environment and run the help:

```commandline
cd Mouse_embryo_analysis_ab_fork
conda activate segmentation 
python tf_extract.py tf-align-simple --help
```

Now, if you're wondering what the `segmentation` environment is, then please follow the instructions here to install it: [Install segmentation python environment](https://github.com/abiswas-odu/roi_convertor#install-on-your-own-machine)





