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
import logging.handlers
from datetime import datetime

PROG = 'Image Summary'
VERSION = '0.1.1'

program_desc = """%(prog)s v%(ver)s:
Gathers data and images for a given subjectcode and presents panels showing: acquisition parameters, post-processed
structural and functional images, and grayordinates results into one file for efficient pipeline QC (of the
FNL_preproc pipeline module).
""" % {'prog': PROG, 'ver': VERSION}

date_stamp = "{:%Y_%m_%d %H:%M}".format(datetime.now())

if not path.exists(path.join(os.getcwd(), 'logs')):
    os.makedirs('logs')

logfile = os.path.join(os.getcwd(), 'logs', 'log-%s.log' % date_stamp)

logging.basicConfig(filename=logfile, level=logging.DEBUG)

_logger = logging.getLogger('Image_Summary_v%s' % VERSION)

# trying out a different format...
fmt = '%(asctime)s %(filename)-8s %(levelname)-8s: %(message)s'

fmt_date = '%Y_%m_%d %H:%M %T%Z'

formatter = logging.Formatter(fmt, fmt_date)

handler = logging.handlers.RotatingFileHandler('_log', backupCount=2)

handler.setFormatter(formatter)

_logger.addHandler(handler)

_logger.info('program log: %s\n' % (date_stamp))


def get_paths(subject_code_path):

    sub_path = path.join(subject_code_path)

    if os.path.exists(sub_path):
        img_path = path.join(sub_path, 'summary')
        data_path = path.join(sub_path, 'unprocessed', 'NIFTI')

        return img_path, data_path


def get_subject_info(path_to_nii_file):
    """
    Much relies upon this function figuring out what sort of file it has been given via file strings.

    Super hacky!
    :param path_to_nii_file: full-path to .nii or .nii.gz
    :return: tuple of subject_code, modality, series
    """

    filename = path.join(path_to_nii_file)

    subject_code, modality, series_num = '', '', ''

    # TODO: fix this up a bit
    if not path.join(path_to_nii_file).endswith('/'):

        filename = path.basename(path_to_nii_file)
    else:
        print '%s is not a file and I reeeally needed a file, not a dir' % filename
        return

    if filename.endswith('.nii.gz'):
        filename = filename.strip('.nii.gz')
    elif filename.endswith('.nii'):
        filename = filename.strip('.nii')

    parts = filename.split('_')

    p_count = len(parts)

    _logger.debug('file string has %d parts' % p_count)

    if p_count <= 2:
        _logger.error('not enough parts for this to be a "good code": %s' % p_count)

    # TODO: needs more checks
    elif p_count == 3 and 'REST' in parts:
        _logger.info('REST file: %s' % parts)
        subject_code = parts[1]
        modality = parts[2]
        series_num = parts[2]

    elif p_count == 3 and 'REST' not in parts:

        subject_code = parts[1]
        modality = 'undefined_modality'
        series_num = parts[2]
        _logger.error('\ncode: %s\nmodality: %s\nseries: %s\n' % (subject_code, modality, series_num))

    elif p_count == 4 and 'SBRef' in parts:

        _logger.info('SBRef file: %s' % parts)

        modality = parts[3]

        series_num = parts[2]

        subject_code = parts[1]

        modality += series_num

    elif p_count == 4 and 'SBRef' not in parts:
        _logger.info('file string parts were: %s' % parts)

        series_num = parts.pop()

        modality = parts.pop()

        if modality == 'T2w' or modality == 'T1w':
            modality += series_num

        if len(parts) == 2:  # parts now 2 fewer and we check what's left

            subject_code = parts[1]

    elif p_count == 5:
        _logger.debug('file parts: %s' % parts)
        subject_code = parts[1]
        modality = parts[3]
        series_num = parts[4]

    elif parts > 5:
        _logger.error('this program will not process such files: %s\ntoo many parts (%s) in the string!' % (filename, len(parts)))
        pass

    return [subject_code, modality, series_num]


def write_csv(data, filepath):
    """
    takes a list of data rows and writes out a csv file to the path provided.

    :param data: list of lists, with each inner-list being one row of data
    :param filepath: path to file-out.csv
    :return: None
    """
    f = open(filepath, 'wb')
    writer = csv.writer(f)
    writer.writerows(data)
    f.close()


def get_nii_info(path_to_nii, info=None):
    """
    Runs fslval on a given nifti file and can take an optional info set.

    :param path_to_nii: full path to nii or nii.gz
    :param info: optional info 3-tuple of subject_code, modality, series
    :return: row of data in a list, length 8
    """

    path_to_nii = os.path.join(path_to_nii)

    if not path.basename(path_to_nii).endswith('.nii.gz'):
        if not path.basename(path_to_nii).endswith('.nii'):
            _logger.error('wrong file type: %s' % path.basename(path_to_nii))
            pass

    _logger.info("getting params on %s\n" % path_to_nii)

    if not info:
        info = get_subject_info(path_to_nii)

    _logger.debug('data-info is: %s' % info)

    modality = info[1]

    cmd = 'echo %s,' % modality
    cmd += '`fslval %s pixdim1`,' % path_to_nii  # x
    cmd += '`fslval %s pixdim2`,' % path_to_nii  # y
    cmd += '`fslval %s pixdim3`,' % path_to_nii  # z
    cmd += '`fslval %s pixdim4`,' % path_to_nii  # TR
    cmd += '`mri_info %s | grep TE | awk %s`,' % (path_to_nii, "'{print $5}'")  # TE
    cmd += '`fslval %s dim4`,' % path_to_nii  # nframes
    cmd += '`mri_info %s | grep TI | awk %s`' % (path_to_nii, "'{print $8}'")

    output = submit_command(cmd)

    data = output.strip("\n").split(',')

    return data


def get_dcm_info(path_to_dicom, modality):
    """
    Runs mri_info on a .dcm to grab TE and other info, giving you: [modality, x,y,z, TR, TE, nFrames, TI]

    :param path_to_dicom: full-path to any single .dcm file
    :param modality: string you want used as a label for this dicom file
    :return: list of data with length 8
    """

    path_to_dicom = os.path.join(path_to_dicom)

    cmd = 'echo %s,' % modality
    cmd += '`mri_info %s | grep "voxel sizes" | awk %s`,' % (path_to_dicom, "'{print $3 $4 $5}'")
    cmd += '`mri_info %s | grep "TE" | awk %s`,' % (path_to_dicom, "'{print $2}'")  # grabs TR
    cmd += '`mri_info %s | grep "TE" | awk %s`,' % (path_to_dicom, "'{print $5}'")
    cmd += '`mri_info %s | grep "nframes" | awk %s`,' % (path_to_dicom, "'{print $7}'")
    cmd += '`mri_info %s | grep "TI" | awk %s`' % (path_to_dicom, "'{print $8}'")

    output = submit_command(cmd)

    data = output.strip("\n").split(',')

    data = [item for item in data if not item == '']

    return data


def grab_te_from_dicom(path_to_dicom):
    """
    We probably do not need this.

    :param path_to_dicom:
    :return: echo time
    """

    path_to_dicom = os.path.join(path_to_dicom)

    cmd = 'echo `mri_info %s | grep "TE" | awk %s`' % (path_to_dicom, "'{print $5}'")

    _logger.debug(cmd)

    output = submit_command(cmd)

    echo_time = output.strip("\n").split(',')

    return echo_time


def submit_command(cmd):
    """
    Takes a string (command-line) and runs it in a sub-shell, collecting either errors or info (output) in logger.

    :param cmd: string (command-line you might otherwise run in a terminal)
    :return: output
    """

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


def get_list_of_data(src_folder):
    """
    Walk through the given directory to find all the nifti data, crudely, to fill lists of t1, t2 and epi-data.

    :param src_folder: directory
    :return: dictionary of lists with full paths to nifti files of interest: t1, t2, epi
    """

    tree = os.walk(src_folder)
    t1_data = []
    t2_data = []
    epi_data = []

    for dir_name in tree:

        _logger.debug('dir: %s' % dir_name[0])

        for file in dir_name[2]:

            if not file.endswith('.nii.gz') and not file.endswith('.nii'):
                continue
            elif 'unused' in path.abspath(file):
                continue
            elif 'cortex' in path.abspath(file):
                continue

            try:
                # TODO: change this to get_subj_info?
                _logger.info('processing nifti file: %s' % file)
                data_info = get_nii_info(path.join(dir_name[0], file))
                modality = data_info[0]

                if 'T1w' in modality or 'T1' == modality:

                    full_path = os.path.join(dir_name[0], file)
                    t1_data.append(full_path)

                elif 'T2w' in modality or 'T2' == modality:

                    full_path = os.path.join(dir_name[0], file)
                    t2_data.append(full_path)

                elif 'SBRef' in modality or 'REST' in modality:

                    full_path = os.path.join(dir_name[0], file)
                    epi_data.append(full_path)

                else:

                    continue

            except IndexError, e:
                _logger.error(e)
                continue

    data_lists = {'t1-data': t1_data, 't2-data': t2_data, 'epi-data': epi_data}

    _logger.debug('\ndata_lists: %s' % data_lists)

    return data_lists


def make_image_dump(src, dst='./img'):
    """
    :param src: path to folder of images
    :param dst: path to dir where images should be placed (need to be picked up by html)
    :return: path to images
    """

    src = os.path.join(src)

    dst = os.path.join(dst)

    if not os.path.exists(dst):
        os.makedirs(dst)


def slice_image_to_ortho_row(file_path, dst):
    """
    Takes path to nifti file and creates an orthogonal row of slices at the mid-lines of brain.

    :param file_path: full path to nifti data
    :param dst: full path including extension
    :return: destination of file-out
    """

    dst = path.join(dst)

    cmd = ''
    cmd += 'slicer %(input_file)s -u -a %(dest)s' % {

        'input_file': path.join(file_path),
        'dest': dst}

    submit_command(cmd)

    return dst


def super_slice_me(nii_gz_path, plane, slice_pos, dst):
    """
    Uses slicer in subprocess to chop given nifti file along the position/plane provided, output to dst.

    :param nii_gz_path: full path to nii.gz file
    :param plane: string = either x/y/or z
    :param dst: destination_path for image_file_out (include your own extensions!)
    :return: path to the sliced outputs
    """

    dst = path.join(dst)

    cmd = ''
    cmd += 'slicer %(input_file)s -u -%(x_y_or_z)s -%(slice_pos)i %(dest)s' % {

        'input_file': path.join(nii_gz_path),
        'x_y_or_z': plane,
        'slice_pos': slice_pos,
        'dest': dst}

    submit_command(cmd)

    return dst


def choose_slices_dict(nifti_file_path):
    """
    Helps decide how to slice-up an image by running 'get_nii_info', which might be a bad idea?

    :param nifti_file_path:
    :return: dict of x/y/z slice positions (to use for slicer)
    """

    nifti_info = get_nii_info(path.join(nifti_file_path))

    if not nifti_info:
        return

    T2_slices = {
        'x': 55,
        'y': 115,
        'z': 145
    }

    T1_slices = {
        'x': 55,
        'y': 115,
        'z': 145

    }

    epi_slices = {
        'x': 55,
        'y': 135,
        'z': 130
    }

    sb_ref_slices = {
        'x': 65,
        'y': 55,
        'z': 45

    }

    if 'SBRef' in nifti_info[0]:
        slices_dict = sb_ref_slices
    elif 'REST' in nifti_info[0]:
        slices_dict = epi_slices
    elif 'T2' in nifti_info[0]:
        slices_dict = T2_slices
    elif 'T1' in nifti_info[0]:
        slices_dict = T1_slices

    return slices_dict


def slice_list_of_data(list_of_data_paths, subject_code=None, dest_dir=None, also_xyz=False):
    """

    :param list_of_data_paths:
    :param dest_dir:
    :return: None
    """

    num = 0

    for i in range(num, len(list_of_data_paths)-1):

        if not dest_dir:
            dest_dir = path.join('./img')
            if not path.exists(dest_dir):
                os.makedirs(dest_dir)

        for datum in list_of_data_paths:
            # TODO: maybe just grab the subject code in args?
            if not subject_code:
                subject_code = get_subject_info(datum)[0]

            slice_image_to_ortho_row(datum, path.join(dest_dir, '%s.png' % subject_code))
            if also_xyz:
                dict = choose_slices_dict(datum)
                for key in dict.keys():

                    print super_slice_me(datum, key, dict[key], os.path.join(dest_dir, '%s_%s-%d.png' %
                                                                                 (subject_code,
                                                                                  key,
                                                                                  dict[key])))


def main():

    parser = argparse.ArgumentParser(description=program_desc)

    # TODO: one at a time for now rather than a list... Still not sure about this.

    parser.add_argument('-i', '--image-path', action="store", dest='img_path', help="Provide a full path to the "
                                                                                     "folder containing all summary "
                                                                                    "images.")

    parser.add_argument('-d', '--data-path', dest='data_path', help="Full path to raw data file.")

    parser.add_argument('-n', '--nii-path', dest='nifti_path', help="Full path to raw nii.gz file.")

    parser.add_argument('-s', '--subject_path', dest='subject_path', help='''
        Path to given subject folder under a given project e.g.
       /remote_home/bucklesh/Projects/TestData/ABCDPILOT_MSC02/''')

    parser.add_argument('-v', '--verbose', dest="verbose", action="store_true", help="Tell me all about it.")

    args = parser.parse_args()

    _logger.debug('args are: %s' % args)

    if args.verbose:
        _logger.setLevel(logging.DEBUG)
    else:
        _logger.setLevel(logging.INFO)

    if args.img_path:

        img_in = os.path.join(args.img_path)

        _logger.info('path to images provided: %s' % img_in)

        _logger.info('list of images:', os.listdir(img_in))

        img_out_path = os.path.join(img_in, 'img')

    else:
        img_out_path = path.join('./img')

    if not path.exists(img_out_path):
        os.makedirs(img_out_path)

    if args.subject_path:
        subject_path = os.path.join(args.subject_path)
        if os.path.exists(subject_path):
            print get_list_of_data(subject_path)

    if args.subject_path:
        subject_path = os.path.join(args.subject_path)
        if os.path.exists(subject_path):
            print get_list_of_data(subject_path)

    param_table = path.join(img_out_path, 'Params.csv')

    # write out the first row of our data rows to setup column headers
    data_rows = [['Modality', 'x', 'y', 'z', 'TR', 'TE', 'frames', 'TI']]

    write_csv(data_rows, param_table)

    if args.nifti_path:

        nii = path.join(args.nifti_path)

        nifti_data = get_nii_info(nii)

        if nifti_data:
            data_rows.append(nifti_data)
            write_csv(data_rows, param_table)

if __name__ == '__main__':

    main()


def rename_structural(path_to_image_dump):
    """
    :param path_to_image_dump: directory containing inputs (will also serve as output dir)
    :return: list of new image (paths)
    """
    structural_imgs = ['temp_13', 'temp_3', 'temp_9', 'temp_14', 'temp_4', 'temp_10']

    new_imgs = []

    for img_label in structural_imgs:

        filename = path.join(path_to_image_dump, img_label, '.png')

        new_file = rename_image(filename)

        new_imgs.append(new_file)

    return new_imgs


def rename_image(img_path):
    """
    :img_path should be full-path to any image file
    :returns renamed, full-path to new image filename
    """

    filename, file_extension = path.splitext(path.basename(img_path))

    if filename in images_dict.keys():
        new_filename = images_dict[filename]

        new_file_path = path.join(path.dirname(img_path), new_filename, file_extension)

        os.rename(img_path, new_file_path)

        return new_file_path


def structural_montage_cmd(list_in, path_out, label=False):
    """
    list_in is a list of image paths
    path_out: output filename (with path)
    label: T or F to decide whether to add labels below each image
    """
    path_out = os.path.join(path_out)

    cmd = 'montage '

    for image_path in list_in:
        input_file = os.path.join(image_path)

        if label:
            cmd += "-label %t "

        cmd += '%s ' % input_file

    # TODO: change to black background

    cmd += '-tile 3x2 -geometry 200x250+0+0 %s/Structural.png' % path_out

    submit_command(cmd)

    return cmd

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
