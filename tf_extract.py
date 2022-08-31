import click
from TF_quant_simple import *
from time import time
from Align_cameras import *

__version__ = "1.2"

@click.group()
def cli():
    pass

@cli.command()
@click.option('--orig_image_dir',required=True,
              type=click.Path(exists=True,file_okay=False,dir_okay=True,readable=True),
              help="Original klb/tif/h5/npy files.")
@click.option('--nucl_seg_dir',required=False, default='',
              type=click.Path(file_okay=False,dir_okay=True,readable=True),
              help="Directory with nuclei segmentation in same format as original images, klb/tif/h5/npy files.")
@click.option('--membrane_seg_dir',required=False, default='',
              type=click.Path(file_okay=False,dir_okay=True,readable=True),
              help="Directory with membrane segmentation in same format as original images, klb/tif/h5/npy files.")
@click.option('--crop_dir',required=True,
              type=click.Path(exists=True,file_okay=False,dir_okay=True,readable=True),
              help="The directory with hpair.csv and vpair.csv generated with generate-cropboxes. "
                   "This is also the OUTPUT directory.")
@click.option("--cropbox_index","-cbi", required=False, default=0, type=click.INT,
              help="The cropbox to visualize for cropping.")
@click.option("--timestamp_min","-tb", required=False, default=0, type=click.INT,
              help="The first timestamp to use for cropping.")
@click.option("--timestamp_max","-te", required=False, default=-1, type=click.INT,
              help="The last timestamp to use for cropping. Setting -1 means use to the last available.")
@click.option("--offset","-of", required=False, default=150, type=click.INT,
              help="The offset used during cropping.")
@click.option("--cell_volume_cutoff", required=True, default=1024, type=click.FLOAT,
              help="The cell volume below which cells are not considered.")
@click.option("--max_margin", required=False, default=2048, type=click.INT,
              help="Original size of images.")
@click.option("--x_shift", required=False, default=-11, type=click.INT,
              help="X shift for camera alignment. For our 210809 data, for Cdx2, Masha found x_shift = -11.")
@click.option("--y_shift", required=False, default=15, type=click.INT,
              help="Y shift for camera alignment. For our 210809 data, for Cdx2, Masha found y_shift = 15")
def tf_align_simple(orig_image_dir, nucl_seg_dir, membrane_seg_dir,  crop_dir, cropbox_index,
                timestamp_min, timestamp_max, offset, cell_volume_cutoff, max_margin, x_shift, y_shift):
    click.echo('Extracting transcription factor intensity...')
    t0 = time()
    mem_tf_vals, nuc_tf_vals, mem_vols, nuc_vols = quantify_tf(orig_image_dir, membrane_seg_dir, nucl_seg_dir, crop_dir,
                                           cropbox_index, cell_volume_cutoff, timestamp_min,
                                           timestamp_max, offset, max_margin, x_shift, y_shift)

    with open(os.path.join(crop_dir,'membrane_tf.csv'), 'w') as f_out:
        f_out.write("Timestamp, Label ID, Mean Label Intensity, Label Volume\n")
        for time_index, labels in mem_tf_vals.items():
            for label_id, intensity in labels.items():
                f_out.write(str(time_index) + ',' + str(label_id) + ',' + str(intensity)
                            + ',' + str(mem_vols[time_index][label_id]) + '\n')

    with open(os.path.join(crop_dir,'nuclei_tf.csv'), 'w') as f_out:
        f_out.write("Timestamp, Label ID, Mean Label Intensity, Label Volume\n")
        for time_index, labels in nuc_tf_vals.items():
            for label_id, intensity in labels.items():
                f_out.write(str(time_index) + ',' + str(label_id) + ',' + str(intensity)
                            + ',' + str(nuc_vols[time_index][label_id]) + '\n')

    t1 = time() - t0
    click.echo('Transcription factor intensity files generated here:' + crop_dir)
    click.echo("Time elapsed: " + str(t1))


@cli.command()
@click.option('--orig_image_file',required=True,
              type=click.Path(exists=True,file_okay=True,dir_okay=False,readable=True),
              help="Original klb/tif/h5/npy file.")
@click.option('--nucl_seg_file',required=False, default='',
              type=click.Path(exists=True,file_okay=True,dir_okay=False,readable=True),
              help="Directory with nuclei segmentation in same format as original images, klb/tif/h5/npy file.")
@click.option('--crop_dir',required=True,
              type=click.Path(exists=True,file_okay=False,dir_okay=True,readable=True),
              help="The directory with hpair.csv and vpair.csv generated with generate-cropboxes. "
                   "This is also the OUTPUT directory.")
@click.option("--cropbox_index","-cbi", required=False, default=0, type=click.INT,
              help="The cropbox to visualize for cropping.")
@click.option("--offset","-of", required=False, default=150, type=click.INT,
              help="The offset used during cropping.")
@click.option("--max_margin", required=False, default=2048, type=click.INT,
              help="Original size of images.")
def align_cam(orig_image_file, nucl_seg_file, crop_dir, cropbox_index, offset, max_margin):
    click.echo('Attempting to align cameras...')
    t0 = time()
    x_shift, y_shift = align_cameras(orig_image_file, nucl_seg_file, crop_dir,
                                           cropbox_index, offset, max_margin)
    print('X-shift:' + str(x_shift))
    print('Y-shift:' + str(y_shift))

    t1 = time() - t0
    click.echo("Time elapsed: " + str(t1))

if __name__ == '__main__':
    cli()
