import click
from TF_quant_simple import *
from time import time
from Align_cameras import *
from ErodeLabels import *

__version__ = "2.2"

@click.group()
def cli():
    pass

@cli.command()
@click.option('--nucl_image_dir',required=True,
              type=click.Path(exists=True,file_okay=False,dir_okay=True,readable=True),
              help="Original nuclei klb/tif/h5/npy files.")
@click.option('--tf_signal_image_dir',required=True,
              type=click.Path(exists=True,file_okay=False,dir_okay=True,readable=True),
              help="TF signal klb/tif/h5/npy files.")
@click.option('--membrane_image_dir',required=False,
              type=click.Path(exists=True,file_okay=False,dir_okay=True,readable=True),
              help="Original uncropped membrane klb/tif/h5/npy files.")
@click.option('--nucl_seg_dir',required=True, default='',
              type=click.Path(exists=True,file_okay=False,dir_okay=True,readable=True),
              help="Directory with nuclei segmentation in same format as original images, klb/tif/h5/npy files.")
@click.option('--membrane_seg_dir', required=False,
              type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
              help="Directory with membrane segmentation in same format as original images, klb/tif/h5/npy files.")
@click.option('--crop_dir', required=False,
              type=click.Path(exists=False, file_okay=False, dir_okay=True, readable=True),
              help="The directory with hpair.csv and vpair.csv generated with generate-cropboxes.")
@click.option('--out_dir',required=True,
              type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
              help="Directory where the extractions will be saved.")
@click.option('--out_prefix', required=True, type=click.STRING,
              help="The prefix of files generated by the extractions.")
@click.option("--cropbox_index","-cbi", required=False, default=0, type=click.INT,
              help="The cropbox to visualize for cropping.")
@click.option("--timestamp_min","-tb", required=False, default=0, type=click.INT,
              help="The first timestamp to use for cropping.")
@click.option("--timestamp_max","-te", required=False, default=-1, type=click.INT,
              help="The last timestamp to use for cropping. Setting -1 means use to the last available.")
@click.option("--rescale", "-rsc", required=True, default=False, type=click.BOOL,
              help="Enable rescaling of the nuclei images before TF extraction.")
@click.option("--offset","-of", required=False, default=150, type=click.INT,
              help="The offset used during cropping.")
@click.option("--cell_volume_cutoff", required=True, default=1024, type=click.FLOAT,
              help="The cell volume below which cells are not considered.")
@click.option("--max_margin", required=False, default=2048, type=click.INT,
              help="Original size of images.")
@click.option("--extract_background", required=False, type=click.BOOL,
              help="Extract the zero label background.")
@click.option("--align_camera", required=True, type=click.BOOL,
              help="Align the camera.")
@click.option("--align_camera_timestamps", required=False, default='', type=click.STRING,
              help="Comma separated list of timestamps to be used to align the camera. " +
                   "Default uses 1st, middle and last images.")
@click.option("--max_absolute_shift", required=False, default=5, type=click.INT,
              help="Absolute MAX shift to explored in X and Y for camera alignment.")
@click.option("--x_shift_override", required=False, default=0, type=click.INT,
              help="X shift for camera alignment. For our 210809 data, for Cdx2, Masha found x_shift = -11.")
@click.option("--y_shift_override", required=False, default=0, type=click.INT,
              help="Y shift for camera alignment. For our 210809 data, for Cdx2, Masha found y_shift = 15")
@click.option("--num_threads", "-n", required=False, default=4, type=click.INT,
              help="The number of threads.")
def tf_align_simple(nucl_image_dir, tf_signal_image_dir, membrane_image_dir, nucl_seg_dir, membrane_seg_dir,
                    crop_dir, out_dir, out_prefix, cropbox_index,
                    timestamp_min, timestamp_max, rescale, offset,
                    cell_volume_cutoff, max_margin, extract_background, align_camera, align_camera_timestamps, max_absolute_shift,
                    x_shift_override, y_shift_override, num_threads):

    # Max. Limits of the shift
    max_abs_alignment_shift = max_absolute_shift
    x_shift = 0
    y_shift = 0

    if align_camera:
        images = [os.path.join(dp, f)
                  for dp, dn, filenames in os.walk(tf_signal_image_dir)
                  for f in filenames if (os.path.splitext(f)[1] == '.klb' or
                                         os.path.splitext(f)[1] == '.h5' or
                                         os.path.splitext(f)[1] == '.tif' or
                                         os.path.splitext(f)[1] == '.npy')]
        images = np.sort(images)

        # Filter images not in timestamp range
        images = filter_timestamp_images(images, timestamp_min, timestamp_max)

        click.echo('Attempting to align cameras...')

        # split columns by ',' and remove whitespace
        if align_camera_timestamps == '':
            align_camera_timestamps_list = [0, int(len(images)/2), len(images) - 1]
        else:
            align_camera_timestamps_list = [int(c.strip()) for c in align_camera_timestamps.split(',')]

        print('Align cameras with timestamps:', align_camera_timestamps_list)
        t0 = time()
        for image_idx in align_camera_timestamps_list:
            if image_idx < len(images):
                file_base, file_prefix, file_ext, time_index = get_filename_components(str(images[image_idx]))
                nucl_seg_file = construct_nucl_file(nucl_seg_dir, file_prefix, file_ext)
                x_shift_i, y_shift_i = align_cameras(str(images[image_idx]), nucl_seg_file, crop_dir,
                                                     cropbox_index, max_abs_alignment_shift,
                                                     offset, max_margin, num_threads)
                print('Image ' + str(time_index) + ' X-shift:' + str(x_shift_i))
                print('Image ' + str(time_index) + ' Y-shift:' + str(y_shift_i))
                x_shift = x_shift + x_shift_i
                y_shift = y_shift + y_shift_i

        x_shift = int(round(x_shift / len(align_camera_timestamps_list), 0))
        y_shift = int(round(y_shift / len(align_camera_timestamps_list), 0))
        print('Mean X-shift:' + str(x_shift))
        print('Mean Y-shift:' + str(y_shift))

        t1 = time() - t0
        click.echo("Time elapsed: " + str(t1))
    else:
        x_shift = x_shift_override
        y_shift = y_shift_override

    click.echo('Extracting transcription factor intensity...')
    t0 = time()
    nuc_tf_vals, nuc_vols = quantify_tf_nucl(tf_signal_image_dir, nucl_seg_dir, crop_dir,
                                           cropbox_index, cell_volume_cutoff, timestamp_min,
                                           timestamp_max, rescale, offset, max_margin,
                                           max_abs_alignment_shift, x_shift, y_shift,
                                           extract_background, num_threads)

    if len(nuc_tf_vals) > 0:
        with open(os.path.join(out_dir, out_prefix + '_nuclei_tf.csv'), 'w') as f_out:
            f_out.write("Timestamp, Label ID, Mean Label Intensity, Label Volume\n")
            for time_index, labels in nuc_tf_vals.items():
                for label_id, intensity in labels.items():
                    f_out.write(str(time_index) + ',' + str(label_id) + ',' + str(intensity)
                                + ',' + str(nuc_vols[time_index][label_id]) + '\n')

    if membrane_image_dir is not None and membrane_seg_dir is not None and \
            os.path.exists(membrane_image_dir) and os.path.exists(membrane_seg_dir):
        mem_tf_vals, mem_vols = quantify_tf_mebrane(membrane_image_dir, membrane_seg_dir, crop_dir,
                                            cropbox_index, cell_volume_cutoff, timestamp_min,
                                            timestamp_max, offset, max_margin,
                                            max_abs_alignment_shift, x_shift, y_shift,
                                            extract_background, num_threads)

        if len(mem_tf_vals) > 0:
            with open(os.path.join(out_dir, out_prefix + '_membrane_tf.csv'), 'w') as f_out:
                f_out.write("Timestamp, Label ID, Mean Label Intensity, Label Volume\n")
                for time_index, labels in mem_tf_vals.items():
                    for label_id, intensity in labels.items():
                        f_out.write(str(time_index) + ',' + str(label_id) + ',' + str(intensity)
                                    + ',' + str(mem_vols[time_index][label_id]) + '\n')

    t1 = time() - t0
    click.echo('Transcription factor intensity files generated here:' + out_dir)
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
@click.option("--num_threads", "-n", required=False, default=4, type=click.INT,
              help="The number of threads.")
def align_cam(orig_image_file, nucl_seg_file, crop_dir,
              cropbox_index, offset, max_margin, num_threads):
    click.echo('Attempting to align cameras...')
    t0 = time()
    x_shift, y_shift = align_cameras(orig_image_file, nucl_seg_file, crop_dir,
                                     cropbox_index, offset, max_margin, num_threads)
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
              type=click.Path(file_okay=False, dir_okay=True, writable=True),
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
