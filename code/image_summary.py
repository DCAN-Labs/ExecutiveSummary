#!/usr/bin/env python
"""
__author__ = 'Shannon Buckley', 12/27/15
"""

import os
import subprocess
import argparse
import csv
from os import path
import logging
from datetime import datetime

PROG = 'Image Summary'
VERSION = '1.0.0'

program_desc = """%(prog)s v%(ver)s:
Gathers data and images for a given subjectcode and presents panels showing: acquisition parameters, post-processed
structural and functional images, and grayordinates results into one file for efficient pipeline QC (of the
FNL_preproc pipeline module).
""" % {'prog': PROG, 'ver': VERSION}

# describes existing set of structural images... may need adjustments to other locations / names
images_dict = {
    'temp_1': 'T1-Axial-InferiorTemporal-Cerebellum',
    'temp_2': 'T2-Axial-InferiorTemporal-Cerebellum',
    'temp_3': 'T1-Axial-BasalGangila-Putamen',
    'temp_4': 'T2-Axial-BasalGangila-Putamen',
    'temp_5': 'T1-Axial-SuperiorFrontal',
    'temp_6': 'T2-Axial-SuperiorFrontal',
    'temp_7': 'T1-Coronal-PosteriorParietal-Lingual',
    'temp_8': 'T2-Coronal-PosteriorParietal-Lingual',
    'temp_9': 'T1-Coronal-Caudate-Amygdala',
    'temp_10': 'T2-Coronal-Caudate-Amygdala',
    'temp_11': 'T1-Coronal-OrbitoFrontal',
    'temp_12': 'T2-Coronal-OrbitoFrontal',
    'temp_13': 'T1-Sagittal-Insula-FrontoTemporal',
    'temp_14': 'T2-Sagittal-Insula-FrontoTemporal',
    'temp_15': 'T1-Sagittal-CorpusCallosum',
    'temp_16': 'T2-Sagittal-CorpusCallosum',
    'temp_17': 'T1-Sagittal-Insula-Temporal-HippocampalSulcus',
    'temp_18': 'T2-Sagittal-Insula-Temporal-HippocampalSulcus'
}


def get_paths(subject_code_path):

    sub_path = os.path.join(subject_code_path)

    if os.path.exists(sub_path):
        img_path = path.join(sub_path, 'summary')
        data_path = path.join(sub_path, 'unprocessed', 'NIFTI')

        return img_path, data_path


def get_subject_info(path_to_nii_file):

    filename = os.path.basename(path_to_nii_file)

    if filename.endswith('.gz'):
        filename = filename.strip('.nii.gz')
    elif filename.endswith('.nii'):
        filename = filename.strip('.nii')

    parts = filename.split('_')

    if len(parts) <= 1:
        _logger.error('parts is too small: %s' % len(parts))
        return parts

    _logger.debug('filename parts were: %s' % parts)

    subject_code = parts[0]

    modality = parts[1]

    series_num = parts[2]

    _logger.info('code: %s\nmodality: %s\nseries: %s\n' % (subject_code, modality, series_num))

    return [subject_code, modality, series_num]


def write_csv(data, filepath):
    f = open(filepath, 'wb')
    writer = csv.writer(f)
    writer.writerows(data)
    f.close()


def get_nii_info(path_to_nii):

    path_to_nii = os.path.join(path_to_nii)

    _logger.info("getting params on %s\n" % path_to_nii)

    info = get_subject_info(path_to_nii)

    _logger.debug('modality is %s' % info)

    modality = info[1]

    cmd = 'echo %s,' % modality
    cmd += '`fslval %s pixdim1`,' % path_to_nii
    cmd += '`fslval %s pixdim2`,' % path_to_nii
    cmd += '`fslval %s pixdim3`,' % path_to_nii
    cmd += '`fslval %s pixdim4`,' % path_to_nii
    cmd += '`mri_info %s | grep TE | awk %s`,' % (path_to_nii, "'{print $5}'")
    cmd += '`fslval %s dim4`,' % path_to_nii
    cmd += '`mri_info %s | grep TI | awk %s`' % (path_to_nii, "'{print $8}'")

    _logger.debug(cmd)

    output = submit_command(cmd)

    data = output.strip("\n").split(',')

    return data


def get_dcm_info(path_to_dicom, modality):

    path_to_dicom = os.path.join(path_to_dicom)

    cmd = 'echo %s,' % modality
    cmd += '`mri_info %s | grep "voxel sizes" | awk %s`,' % (path_to_dicom, "'{print $3 $4 $5}'")
    cmd += '`mri_info %s | grep "TE" | awk %s`,' % (path_to_dicom, "'{print $2}'")
    cmd += '`mri_info %s | grep "TE" | awk %s`,' % (path_to_dicom, "'{print $5}'")
    cmd += '`mri_info %s | grep "nframes" | awk %s`,' % (path_to_dicom, "'{print $7}'")
    cmd += '`mri_info %s | grep "TI" | awk %s`' % (path_to_dicom, "'{print $8}'")

    _logger.debug(cmd)

    output = submit_command(cmd)

    data = output.strip("\n").split(',')

    data = [item for item in data if not item == '']

    return data


def grab_te_from_dicom(path_to_dicom):

    path_to_dicom = os.path.join(path_to_dicom)

    cmd = 'echo `mri_info %s | grep "TE" | awk %s`' % (path_to_dicom, "'{print $5}'")

    _logger.debug(cmd)

    output = submit_command(cmd)

    echo_time = output.strip("\n").split(',')

    return echo_time


def submit_command(cmd):

    _logger.debug(cmd)

    proc = subprocess.Popen(
        cmd
        , shell=True
        , stdout=subprocess.PIPE
        , stderr=subprocess.PIPE
    )

    (output, error) = proc.communicate()

    if error:
        _logger.error(error)
    if output:
        _logger.info(output)

    return output


def get_list_of_data(src):

    tree = os.walk(src)
    t1_data = []
    t2_data = []
    epi_data = []

    for dir in tree:

        for file in dir[2]:

            if not (file.endswith('.gz') or file.endswith('.nii')):
                continue

            try:

                if get_subject_info(file)[1] == 'T1w':

                    full_path = os.path.join(dir[0], file)
                    t1_data.append(full_path)

                elif get_subject_info(file)[1] == 'T2w':

                    full_path = os.path.join(dir[0], file)
                    t2_data.append(full_path)

                elif get_subject_info(file)[1].__contains__('REST'):

                    full_path = os.path.join(dir[0], file)
                    epi_data.append(full_path)

            except IndexError, e:
                _logger.error(e)
                continue

    data_lists = [t1_data, t2_data, epi_data]
    _logger.info('\ndata_lists: %s' % data_lists)

    return data_lists


def make_image_dump(src, dst):
    src = os.path.join(src)
    pass


def super_slice_me(nii_gz_path, plane, slice_pos, dst):
    """
    :param nii_gz_path: full path to nii.gz file
    :param x: default slice position in the x-plane (Sagittal on T1)
    :param y: default slice position in y-plane (Coronal on T1)
    :param z: default slice position in the z-plane (Axial on T1)
    :param dst: destination for files.
    :return: nothing, or a path to the sliced outputs? Or a tuple of path(s)?
    """

    cmd = ''
    cmd += 'slicer %(input_file)s -u -%(x_y_or_z)s -%(slice_pos)i %(dest)s' % {

        'input_file': nii_gz_path,
        'x_y_or_z': plane,
        'slice_pos': slice_pos,
        'dest': dst}

    submit_command(cmd)


def main():

    parser = argparse.ArgumentParser(description=program_desc)

    # TODO: one at a time for now rather than a list... Still not sure about this.

    parser.add_argument('-i', '--image-path', action="store", dest='img_path', help="Provide a full path to the "
                                                                                     "folder "
                                                                                     "containing all summary images.")

    parser.add_argument('-d' '--data-path', dest='data_path', help="Full path to raw data file.")

    parser.add_argument('-n' '--nii-path', dest='nifti_path', help="Full path to raw nii.gz file.")

    parser.add_argument('-s', '--subject_path', dest='project_path', help='''
        Path to given subject folder under a given project e.g.
       /remote_home/bucklesh/Projects/TestData/ABCDPILOT_MSC02/''')

    parser.add_argument('-v', '--verbose', dest="verbose", action="store_true", help="Tell me all about it.")

    args = parser.parse_args()

    _logger.debug('args are: %s' % args)

    if args.verbose:
        _logger.setLevel(logging.DEBUG)
    else:
        _logger.setLevel(logging.INFO)

    if not args.img_path.endswith('/'):
       args.img_path += '/'

    img_in = os.path.join(args.img_path)

    _logger.debug('path to images: %s' % img_in)
    _logger.debug(os.listdir(img_in))

    out_path = os.path.join(img_in)

    param_table = os.path.join(out_path + 'Params.csv')

    # write out the first row of our data rows to setup column headers
    data_rows = [['Modality', 'x', 'y', 'z', 'TR', 'TE', 'frames', 'TI']]

    write_csv(data_rows, param_table)


if __name__ == '__main__':

    date_stamp = "{:%Y_%m_%d_%H:%M}".format(datetime.now())

    logfile = os.path.join(os.getcwd(), 'log-%s.log' % date_stamp)

    logging.basicConfig(filename=logfile, level=logging.DEBUG)

    _logger = logging.getLogger()

    _logger.info('%s_v%s: ran on %s\n' % (PROG, VERSION, date_stamp))

    main()


def rename_structural(path_to_image_dump):
    structural_imgs = ['temp_13', 'temp_3', 'temp_9', 'temp_14', 'temp_4', 'temp_10']

    new_imgs = []

    for img_label in structural_imgs:
        filename = os.path.join(path_to_image_dump, img_label, '.png')

        new_file = rename_image(filename)

        new_imgs.append(new_file)

    return new_imgs


def rename_image(img_path):
    """:arg img_path should be full-path to any image file
        :returns renamed, full-path to new image filename"""

    filename, file_extension = path.splitext(path.basename(img_path))

    if filename in images_dict.keys():
        new_filename = images_dict[filename]

        new_file_path = path.join(path.dirname(img_path), new_filename, file_extension)

        os.rename(img_path, new_file_path)

        return new_file_path


# reportlab stuff
# TODO: do we really want to build montages and/or use Reportlab?
def structural_montage_cmd(path_in, path_out):
    """path_in is a full-path to the set of structural images, path_out to where
    you want the montage to be placed.
    :returns the command_line for ImageMagick"""

    path_out = os.path.join(path_out)

    cmd = 'montage '

    for png in rename_structural(path_in):
        input_file = os.path.join(png)

        cmd += "-label %t "
        cmd += '%s ' % input_file

    cmd += '-tile 3x2 -geometry 200x250>+2+2 %s/Structural.png' % path_out

    return cmd
