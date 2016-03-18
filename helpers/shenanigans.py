#!/usr/bin/env python

import os
from os import path
import subprocess


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


def get_dcm_info(path_to_dicom, modality=None):
    """
    Runs mri_info on a .dcm to grab TE and other info, giving you: [modality, x,y,z, TR, TE, nFrames, TI]

    :param path_to_dicom: full-path to any single .dcm file
    :param modality: string you want used as a label for this dicom file
    :return: list of data with length 8
    """

    path_to_dicom = path.join(path_to_dicom)

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


def structural_montage_cmd(list_in, path_out, label=False):
    """
    list_in is a list of image paths
    path_out: output filename (with path)
    label: T or F to decide whether to add labels below each image
    """
    path_out = path.join(path_out)

    cmd = 'montage '

    for image_path in list_in:
        input_file = path.join(image_path)

        if label:
            cmd += "-label %t "

        cmd += '%s ' % input_file

    # TODO: change to black background

    cmd += '-tile 3x2 -geometry 200x250+0+0 %s/Structural.png' % path_out

    return cmd


def submit_command(cmd):
    """
    Takes a string (command-line) and runs it in a sub-shell, collecting either errors or info (output) in logger.

    :param cmd: string (command-line you might otherwise run in a terminal)
    :return: output
    """

    proc = subprocess.Popen(
        cmd
        , shell=True
        , stdout=subprocess.PIPE
        , stderr=subprocess.PIPE
    )

    (output, error) = proc.communicate()

    if error:
        print 'error! %s' % error
    if output:
        print 'output: %s' % output

    return output


def grab_te_from_dicom(path_to_dicom):
    """
    We probably do not need this.

    :param path_to_dicom:
    :return: echo time
    """

    path_to_dicom = os.path.join(path_to_dicom)

    cmd = 'echo `mri_info %s | grep "TE" | awk %s`' % (path_to_dicom, "'{print $5}'")

    output = submit_command(cmd)

    echo_time = output.strip("\n").split(',')

    return echo_time

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