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
import sys
sys.path.append('/group_shares/PSYCH/code/release/utilities/executive_summary')
from helpers import shenanigans

PROG = 'Image Summary'
VERSION = '0.7.0'

program_desc = """%(prog)s v%(ver)s:
Gathers data and images for a given subjectcode and presents panels showing: acquisition parameters, post-processed
structural and functional images, and grayordinates results into one file for efficient QC (of the
FNL_preproc pipeline).
""" % {'prog': PROG, 'ver': VERSION}

date_stamp = "{:%Y_%m_%d_%H_%M}".format(datetime.now())

if not path.exists(path.join(os.getcwd(), 'logs')):
    os.makedirs('logs')

logfile = os.path.join(os.getcwd(), 'logs', 'log-%s.log' % date_stamp)

logging.basicConfig(filename=logfile, level=logging.ERROR)

_logger = logging.getLogger('Image_Summary_v%s' % VERSION)

# trying out a different format...
fmt = '%(asctime)s %(filename)-8s %(levelname)-8s: %(message)s'

fmt_date = '%Y_%m_%d %H:%M %T%Z'

formatter = logging.Formatter(fmt, fmt_date)

handler = logging.handlers.RotatingFileHandler('_log', backupCount=2)

handler.setFormatter(formatter)

_logger.addHandler(handler)

_logger.info('\nprogram log: %s' % (date_stamp))


def get_paths(subject_code_path):
    """
    PLACEHOLDER Takes subj_path and returns all relevant paths
    :param subject_code_path:
    :return: list or dict for all paths needed for processing exec summary
    """

    sub_path = path.join(subject_code_path)
    _logger.debug('\nsubject path is %s\n' % sub_path)

    #print '\n%s // %s // %s \n' % (sub_path.split('/')[-4], sub_path.split('/')[-3], sub_path.split('/')[-2])

    if path.exists(sub_path):

        img_in_path = path.join(sub_path, 'summary')

        _logger.debug('\nimages in : %s\n' % img_in_path)

        data_path = path.join(sub_path, 'unprocessed', 'NIFTI')
        _logger.debug('\ndata are in : %s\n' % data_path)

        return img_in_path, data_path
    else:
        _logger.error('\npath does not exist: %s' % sub_path)


def get_subject_info(path_to_nii_file):
    """
    Takes path to nii or nii.gz file and returns a list of 3 elements: subjID, modality, series.

    Super hacky!
    :param path_to_nii_file: full-path to .nii or .nii.gz
    :return: list of subject_code, modality, series
    """

    filename = path.join(path_to_nii_file)

    subject_code, modality, series_num = '', '', ''

    # TODO: fix this up a bit
    if not path.join(path_to_nii_file).endswith('/'):

        filename = path.basename(path_to_nii_file)
        dirname = path.dirname(path_to_nii_file)
    else:
        print '%s is not a file and I reeeally needed a file, not a dir' % filename
        _logger.error('\n%s is not a file...' % filename)
        return

    if filename.endswith('.nii.gz'):
        filename = filename.strip('.nii.gz')
    elif filename.endswith('.nii'):
        filename = filename.strip('.nii')
    else:
        print '%s is neither .nii nor nii.gz' % filename
        return

    parts = filename.split('_')

    p_count = len(parts)

    _logger.debug('file string has %d parts: %s' % (p_count, parts))

    if p_count < 2:
        _logger.error('not enough file string parts for this to be a "good summary": %s' % p_count)

    elif p_count == 2 and 'Scout' in parts:

        _logger.info('raw SBRef file: %s' % parts)
        subject_code = parts[0]  # Needs to come from somewhere else given our scheme for pulling code from files
        modality = 'SBRef'

        series_num = path.basename(path.dirname(path_to_nii_file))[-1]
        # print 'series_num: %s' % series_num

    elif p_count == 2 and 'SBRef' in parts[1]:

        _logger.info('raw SBRef file: %s' % parts)
        subject_code = parts[0]  # Needs to come from somewhere else given our scheme for pulling code from files
        modality = parts[1]
        series_num = parts[0]

    elif p_count == 2 and 'REST' in parts[1][0:4]:

        _logger.info('raw REST file: %s' % parts)
        subject_code = parts[0]
        modality = parts[1]
        series_num = parts[1]

    # to support ABCDPILOT_MSC02 type of subjectIDs with raw REST data... we hack
    elif p_count == 3 and 'SBRef' not in parts and 'REST' in parts[-1][0:4]:

        _logger.info('raw REST file: %s' % parts)
        subject_code = parts[0] + '_' + parts[1]
        modality = parts[2]
        series_num = parts[2]

    elif p_count == 3 and 'T1w' in parts:

        _logger.info('T1 file: %s' % parts)
        subject_code = parts[0]
        modality = parts[1]
        series_num = parts[2]

    elif p_count == 3 and 'T2w' in parts:

        _logger.info('T2 file: %s' % parts)
        subject_code = parts[0]
        modality = parts[1]
        series_num = parts[2]

    elif p_count == 4 and 'SBRef' in parts:

        _logger.info('SBRef file: %s' % parts)
        modality = parts[3]
        series_num = parts[2]
        subject_code = parts[1]
        modality += '_' + series_num

    elif p_count == 4 and 'SBRef' not in parts:

        _logger.info('file string parts were: %s' % parts)
        series_num = parts.pop()
        modality = parts.pop()

        if modality == 'T2w' or modality == 'T1w':

            modality += series_num

        if len(parts) == 2:  # parts now 2 fewer and we check what's left

            subject_code = parts[1]

    elif p_count == 5:

        _logger.info('file parts: %s' % parts)
        subject_code = parts[1]
        modality = parts[3]
        series_num = parts[4]

    elif parts > 5:
        _logger.error('this program will not process such files: %s\ntoo many parts (%s) in the string!' % (filename, len(parts)))
        _logger.error('\nimage_summary: %s\nmodality: %s\nseries: %s\n' % (subject_code, modality, series_num))
        pass

    return [subject_code, modality, series_num]


def write_csv(data, filepath):
    """
    Takes a list of data rows and writes out a csv file to the path provided.

    :parameter: data: list of lists, with each inner-list being one row of data
    :parameter: filepath: path to file-out.csv
    :return: None
    """
    f = open(filepath, 'wb')
    writer = csv.writer(f)
    writer.writerows(data)
    f.close()


def get_nii_info(path_to_nii, info=None):
    """
    Runs fslval on a given nifti file and can take an optional info set.

    :parameter: path_to_nii: full path to nii or nii.gz
    :parameter: info: optional info LIST of 3 items: subject_code, modality, series
    :return: row of data in a list, length 8
    """

    path_to_nii = path.join(path_to_nii)

    if not path.basename(path_to_nii).endswith('.nii.gz'):
        if not path.basename(path_to_nii).endswith('.nii'):
            _logger.error('\nwrong file type: %s' % path.basename(path_to_nii))
            return

    _logger.info("\ngetting params on %s\n" % path_to_nii)

    if not info:
        info = get_subject_info(path_to_nii)

    _logger.debug('\ndata-info is: %s\n' % info)

    try:

        modality = info[1]

    except TypeError:

        print '\n--->%s... is the wrong file type<---' % path.join(path_to_nii)

    if modality == '':
        modality = 'UnknownModality'

    cmd = 'echo %s,' % modality
    cmd += '`fslval %s pixdim1`,' % path_to_nii  # x
    cmd += '`fslval %s pixdim2`,' % path_to_nii  # y
    cmd += '`fslval %s pixdim3`,' % path_to_nii  # z

    # TODO: need to point mri_info at a .dcm file in order to pull TE

    cmd += '`mri_info %s | grep TE | awk %s`,' % (path_to_nii, "'{print $5}'")  # TE via mri_info
    cmd += '`mri_info %s | grep TR | awk %s`,' % (path_to_nii, "'{print $2}'")  # TR
    cmd += '`fslval %s dim4`,' % path_to_nii  # nframes
    cmd += '`mri_info %s | grep TI | awk %s`' % (path_to_nii, "'{print $8}'")  # TI via mri_info

    output = submit_command(cmd)

    output = output.strip('\n').split(',')

    modality = output[0]

    floats_list = []

    for value in output[1:]:

        floats_list.append(format(float(value), '.2f'))

    data = [modality] + floats_list

    #print data

    return data


def submit_command(cmd):
    """
    Takes a string (command-line) and runs it in a sub-shell, collecting either errors or info (output) in logger.

    :param cmd: string (command-line you might otherwise run in a terminal)
    :return: output from the command that ran
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
    Walks through the given directory to find all the nifti data, crudely, to fill lists of t1, t2 and epi-data.

    :param src_folder: directory (the /summary folder for a given participant's data)
    :return: dictionary of lists with full paths to nifti files of interest: t1, t2, epi
    """

    tree = os.walk(src_folder)
    t1_data = []
    t2_data = []
    epi_data = []

    for dir_name in tree:

        _logger.debug('dir: %s' % dir_name[0])

        for file in dir_name[2]:
            # limit which files are processed...

            if not file.endswith('.nii.gz') and not file.endswith('.nii'):
                continue
            elif 'unused' in path.abspath(file):
                continue
            elif 'cortex' in path.abspath(file):
                continue
            elif 'FieldMap' in path.abspath(file):
                continue

            _logger.info('processing nifti file: %s' % file)

            try:

                data_info = get_nii_info(path.join(dir_name[0], file))

                modality = data_info[0]

                if 'T1w' in modality or 'T1' == modality:

                    full_path = path.join(dir_name[0], file)
                    t1_data.append(full_path)

                elif 'T2w' in modality or 'T2' == modality:

                    full_path = path.join(dir_name[0], file)
                    t2_data.append(full_path)

                elif 'SBRef' in modality or 'REST' in modality:

                    full_path = path.join(dir_name[0], file)
                    epi_data.append(full_path)

                else:

                    continue

            except IndexError, e:
                _logger.error(e)
                continue

    data_lists = {'t1-data': t1_data, 't2-data': t2_data, 'epi-data': epi_data}

    if 'SBRef' not in data_lists['epi-data'][-1:]:  # either of the last two paths in list
        print 'no SBRef data in epi-data list'
        _logger.info('missing SBRef data from /unprocessed/NIFTI... pulling from alternative')

    _logger.debug('\ndata_lists: %s' % data_lists)

    return data_lists


def slice_image_to_ortho_row(file_path, dst):
    """
    Takes path to nifti file and writes out an orthogonal row of slices at the mid-points of the image volume to dst.

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


def choose_slices_dict(nifti_file_path, subj_code=None, nii_info=None):
    """
    Helps decide how to slice-up an image by running 'get_nii_info', which might be a bad idea?

    :param nifti_file_path:
    :param subj_code: optional subject_code can be passed-in to speed things along
    :return: dict of x/y/z slice positions (to use for slicer)
    """

    nifti_info = get_nii_info(path.join(nifti_file_path))

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

    # TODO: choose better slices!
    raw_rest_slices = {
        'x': 65,
        'y': 55,
        'z': 45
    }

    sb_ref_slices = {
        'x': 65,
        'y': 55,
        'z': 45
    }

    if 'SBRef' in nifti_info[0]:  # grab these first since they may also contain 'REST' in their strings
        slices_dict = sb_ref_slices
    elif 'REST' in nifti_info[0]:  # then grab all the remaining 'REST' data that do not have 'SBRef' in string
        slices_dict = raw_rest_slices
    elif 'T2' in nifti_info[0]:
        slices_dict = T2_slices
    elif 'T1' in nifti_info[0]:
        slices_dict = T1_slices
    else:
        print 'not in the standard set of slices...\nDefaulting to T1 slices'
        slices_dict = T1_slices

    return slices_dict


def slice_list_of_data(list_of_data_paths, subject_code=None, modality=None, dest_dir=None, also_xyz=False):
    """
    Takes list of data paths and other options to decide how to slice them all up.

    :param list_of_data_paths: a list containing full-path strings
    :param subject_code: optional string. faster function if known & can pass?
    :param dest_dir: destination dir for the images to be produced & gathered
    :param also_xyz: boolean as to whether or not you also want to create x-y-z, individual planes of sliced images.
    :return: None
    """

    num = 0

    for i in range(num, len(list_of_data_paths)):

        if not dest_dir:
            dest_dir = path.join('./img')
            if not path.exists(dest_dir):
                os.makedirs(dest_dir)

        for datum in list_of_data_paths:

            if not subject_code:
                subject_code = get_subject_info(datum)

            if modality:
                slice_image_to_ortho_row(datum, path.join(dest_dir, '%s.png' % (modality)))
            else:
                slice_image_to_ortho_row(datum, path.join(dest_dir, '%s.png' % subject_code))

            if also_xyz:
                dict = choose_slices_dict(datum, subject_code)
                for key in dict.keys():

                    print super_slice_me(datum, key, dict[key], os.path.join(dest_dir, '%s_%s-%d.png' %
                                                                                 (modality,
                                                                                  key,
                                                                                  dict[key])))


def main():

    parser = argparse.ArgumentParser(description=program_desc)

    parser.add_argument('-d', '--dicom-path', dest='dicom_path', help="Uses mri_info to grab params via the given full "
                                                                      "path to any single, raw dicom file.")

    parser.add_argument('-n', '--nii-path', dest='nifti_path', help="Uses fslval to grab params via the given full "
                                                                    "path to any nii or nii.gz file.")

    parser.add_argument('--verbose', dest="verbose", action="store_true", help="Tell me all about it.")

    parser.add_argument('-vv', '--very_verbose', dest="very_verbose", action="store_true", help="Tell me all about it.")

    args = parser.parse_args()

    _logger.debug('args are: %s' % args)

    # write out the first row of our data rows to setup column headers
    data_rows = [['Modality', 'x', 'y', 'z', 'TE', 'TR', 'frames', 'TI']]

    if args.verbose:
        _logger.setLevel(logging.INFO)
    elif args.very_verbose:
        _logger.setLevel(logging.DEBUG)
    else:
        _logger.setLevel(logging.ERROR)

    if args.dicom_path:
        dcm_path = path.join(args.dicom_path)
        if path.exists(dcm_path):
            dcm_params = shenanigans.get_dcm_info(dcm_path)

            print 'parameters are: %s ' % dcm_params
            return dcm_params
        else:
            _logger.error('path does not exist: \n\t%s ' % dcm_path)
            print 'oops that path is no good!'

    if args.nifti_path:
        nifti_path = path.join(args.nifti_path)
        if path.exists(nifti_path):
            nii_params = get_nii_info(nifti_path)
            data_rows.append(nii_params)
            print 'parameters are: %s ' % data_rows
            param_table = path.join(os.path.dirname(nifti_path), 'Params.csv')
            data_rows.append(nii_params)
            write_csv(data_rows, param_table)
        else:
            _logger.error('path does not exist: \n\t%s ' % nifti_path)
            print 'oops that path is no good!'


if __name__ == '__main__':

    main()
