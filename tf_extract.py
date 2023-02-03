import click
from TF_quant_simple import *
from time import time
from Align_cameras import *
from Label_read import *
from ErodeLabels import *

__version__ = "1.4"

@click.group()
def cli():
    pass

@cli.command()
@click.option('--orig_image_dir',required=True,
              type=click.Path(exists=True,file_okay=False,dir_okay=True,readable=True),
              help="Original klb/tif/h5/npy files.")
@click.option('--nucl_seg_dir',required=True, default='',
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
@click.option("--align_camera", required=True, type=click.BOOL,
              help="Align the camera.")
@click.option("--x_shift_override", required=False, default=0, type=click.INT,
              help="X shift for camera alignment. For our 210809 data, for Cdx2, Masha found x_shift = -11.")
@click.option("--y_shift_override", required=False, default=0, type=click.INT,
              help="Y shift for camera alignment. For our 210809 data, for Cdx2, Masha found y_shift = 15")
def tf_align_simple(orig_image_dir, nucl_seg_dir, membrane_seg_dir,  crop_dir, cropbox_index,
                timestamp_min, timestamp_max, offset, cell_volume_cutoff, max_margin, align_camera,
                    x_shift_override, y_shift_override):

    x_shift = 0
    y_shift = 0
    if align_camera:
        images = [os.path.join(dp, f)
                  for dp, dn, filenames in os.walk(orig_image_dir)
                  for f in filenames if (os.path.splitext(f)[1] == '.klb' or
                                         os.path.splitext(f)[1] == '.h5' or
                                         os.path.splitext(f)[1] == '.tif' or
                                         os.path.splitext(f)[1] == '.npy')]
        images = np.sort(images)

        click.echo('Attempting to align cameras...')
        t0 = time()
        image_1_idx = 0
        cur_name = os.path.basename(str(images[image_1_idx]))
        file_prefix = os.path.splitext(cur_name)[0]
        file_ext = os.path.splitext(cur_name)[1]
        nucl_seg_file = construct_nucl_file(nucl_seg_dir, file_prefix, file_ext)
        x_shift_1, y_shift_1 = align_cameras(str(images[image_1_idx]), nucl_seg_file, crop_dir,
                                         cropbox_index, offset, max_margin)

        print('Image 0 X-shift:' + str(x_shift_1))
        print('Image 0 Y-shift:' + str(y_shift_1))

        image_mid_idx = int(len(images)/2)
        cur_name = os.path.basename(images[image_mid_idx])
        file_prefix = os.path.splitext(cur_name)[0]
        file_ext = os.path.splitext(cur_name)[1]
        nucl_seg_file = construct_nucl_file(nucl_seg_dir, file_prefix, file_ext)
        x_shift_2, y_shift_2 = align_cameras(str(images[image_mid_idx]), nucl_seg_file, crop_dir,
                                             cropbox_index, offset, max_margin)

        print('Image ' + str(image_mid_idx) + ' X-shift:' + str(x_shift_2))
        print('Image ' + str(image_mid_idx) + ' Y-shift:' + str(y_shift_2))

        image_n_idx = len(images) - 1
        cur_name = os.path.basename(images[image_n_idx])
        file_prefix = os.path.splitext(cur_name)[0]
        file_ext = os.path.splitext(cur_name)[1]
        nucl_seg_file = construct_nucl_file(nucl_seg_dir, file_prefix, file_ext)
        x_shift_3, y_shift_3 = align_cameras(str(images[image_n_idx]), nucl_seg_file, crop_dir,
                                             cropbox_index, offset, max_margin)

        print('Image ' + str(image_n_idx) + ' X-shift:' + str(x_shift_3))
        print('Image ' + str(image_n_idx) + ' Y-shift:' + str(y_shift_3))

        x_shift = round((x_shift_1 + x_shift_2 + x_shift_3) / 3, 0)
        y_shift = round((y_shift_1 + y_shift_2 + y_shift_3) / 3, 0)
        print('X-shift:' + str(x_shift))
        print('Y-shift:' + str(y_shift))

        t1 = time() - t0
        click.echo("Time elapsed: " + str(t1))
    else:
        x_shift = x_shift_override
        y_shift = y_shift_override

    click.echo('Extracting transcription factor intensity...')
    t0 = time()
    mem_tf_vals, nuc_tf_vals, mem_vols, nuc_vols = quantify_tf(orig_image_dir, membrane_seg_dir, nucl_seg_dir, crop_dir,
                                           cropbox_index, cell_volume_cutoff, timestamp_min,
                                           timestamp_max, offset, max_margin, x_shift, y_shift)

    if len(mem_tf_vals)>0:
        with open(os.path.join(crop_dir,'membrane_tf.csv'), 'w') as f_out:
            f_out.write("Timestamp, Label ID, Mean Label Intensity, Label Volume\n")
            for time_index, labels in mem_tf_vals.items():
                for label_id, intensity in labels.items():
                    f_out.write(str(time_index) + ',' + str(label_id) + ',' + str(intensity)
                                + ',' + str(mem_vols[time_index][label_id]) + '\n')

    if len(nuc_tf_vals)>0:
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

@cli.command()
@click.option('--orig_image_dir',required=True,
              type=click.Path(exists=True,file_okay=False,dir_okay=True,readable=True),
              help="Original klb/tif/h5/npy files.")
@click.option('--nucl_seg_dir',required=True, default='',
              type=click.Path(file_okay=False,dir_okay=True,readable=True),
              help="Directory with nuclei segmentation in same format as original images, klb/tif/h5/npy files.")
@click.option('--out_dir',required=False, default='.',
              type=click.Path(file_okay=False,dir_okay=True,readable=True),
              help="Directory where the eroded labels and contours will bne saved.")
@click.option("--footprint_size","-fp", required=False, default=3, type=click.INT,
              help="The footprint used during erosion.")
@click.option("--gen_contour", "-gc", is_flag=True,
              help="Generate RGB contour image with the eroded label drawn into the image.")
def erode_labels(orig_image_dir, nucl_seg_dir, out_dir, footprint_size, gen_contour):
    click.echo('Attempting to erode labels...')
    t0 = time()
    images = [os.path.join(dp, f)
              for dp, dn, filenames in os.walk(orig_image_dir)
              for f in filenames if (os.path.splitext(f)[1] == '.klb' or
                                     os.path.splitext(f)[1] == '.h5' or
                                     os.path.splitext(f)[1] == '.tif' or
                                     os.path.splitext(f)[1] == '.npy')]
    for image in images:
        erode_image_labels(image, nucl_seg_dir, out_dir, footprint_size, gen_contour)
    t1 = time() - t0
    click.echo("Time elapsed: " + str(t1))

if __name__ == '__main__':
    cli()
