# Mouse_embryo_analysis

## Extracting transcription factor signal

Load the `segmentation` conda environment and run the help:

```commandline
conda activate segmentation 
python tf_extract.py tf-align-simple --help
```

Now, if you're wondering what the segmentation environment is, then please follow the instructions here to install it: [Install segmentation python environment](https://github.com/abiswas-odu/roi_convertor#install-on-your-own-machine)

Executing the program requires using the commandline and parameters:

```commandline
python tf_extract.py tf-align-simple --orig_image_dir <dir> --nucl_seg_dir <label_dir> --crop_dir <crop_dir> --cropbox_index 7 --timestamp_min 0 --timestamp_max 10 --offset 150 --cell_volume_cutoff 2000
```

See --help for all the other parameters.