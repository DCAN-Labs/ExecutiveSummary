#! /home/exacloud/lustre1/fnl_lab/code/external/utilities/anaconda2/bin/python
"""
__author__ = 'Shannon Buckley', 12/27/15
"""

import os
from os import path
import subprocess


def rename_structural(path_to_image_dump):
    """
    Takes list of unlabeled png and renames them in-place.
    :param path_to_image_dump: directory containing inputs (will also serve as output dir)
    :return: list of new image paths
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
    Takes an image path, renames it according to images_dict.

    :img_path should be full-path to any image file
    :returns renamed, full-path to new image filename
    """

    filename, file_extension = path.splitext(path.basename(img_path))

    if filename in images_dict.keys():
        new_filename = images_dict[filename]

        new_file_path = path.join(path.dirname(img_path), new_filename, file_extension)

        os.rename(img_path, new_file_path)

        return new_file_path


def get_dcm_info(path_to_dicom, path_to_nii, modality=None):
    """
    Runs mri_info on a .dcm to grab TE and other info, giving you: [modality, x,y,z, TE, TR, nFrames, TI]

    :param path_to_dicom: full-path to any single .dcm file
    :param path_to_nii: needs path to nifti to get correct number of frames and TR
    :param modality: optional string you want used as a label for this dicom file
    :return: list of data with length 8
    """

    path_to_dicom = path.join(path_to_dicom)

    if modality == '':
        modality = 'UnknownModality'

    final_data = [modality]

    if path_to_dicom is not None:

        cmd = 'echo %s,' % modality
        cmd += '`mri_info %s | grep "voxel sizes" | awk %s`,' % (path_to_dicom, "'{print $3 $4 $5}'")
        cmd += '`mri_info %s | grep "TE" | awk %s`,' % (path_to_dicom, "'{print $5}'")  # grabs TE
        cmd += '`mri_info %s | grep TR | awk %s`,' % (path_to_nii, "'{print $2}'")  # TR
        cmd += '`fslval %s dim4`,' % path_to_nii  # nframes
        cmd += '`mri_info %s | grep "TI" | awk %s`' % (path_to_dicom, "'{print $8}'")

        output = submit_command(cmd)

        output = output.strip("\n").split(',')

        for value in output[1:]:
            try:
                value = format(float(value), '.2f')
            
            # If there is non-number input, format or remove it
            except ValueError:
                if value.isdigit():
                    value = format(float(filter(lambda x: x.isdigit(), value)), '.2f')
                else:
                     value = 'Not found'

            final_data.append(value)

    return final_data


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
    :param path_to_dicom:
    :return: echo time
    """

    path_to_dicom = os.path.join(path_to_dicom)

    cmd = 'echo `mri_info %s | grep "TE" | awk %s`' % (path_to_dicom, "'{print $5}'")
    print cmd

    output = submit_command(cmd)
    print output

    echo_time = output.strip("\n").split(',')
    print echo_time

    return format(float(echo_time), '.2f')


def update_user(info):
    """
    Print prettily for user.

    :parameter: info: string
    :return: None
    """

    print '\n%s\n' % info


def read_list_file(path_to_file):
    """
    Takes path to a file with one line per processed-dataset you want to check.

    :parameter: path_to_file: path to the list_file.txt
    :return: list of lines from the file
    """

    with open(path_to_file, 'r') as f:

        lines_in_file = f.readlines()

        f.close()

    return lines_in_file


def handle_trailing_slash(directory):
    """
    Takes a directory and returns it back without any trailing slash, if present.

    :parameter directory: path to a directory with or without a trailing slash (you don't have to know which)
    :return: directory path without trailing slash
    """

    if path.join(directory).endswith('/'):

        return directory.rstrip('/')
    else:
        return path.join(directory)


def get_airc_dicom_path_from_nifti_info(processed_subject_path, modality_name):
    """
    Uses another helper function to find a dicom path for a given nifti modality and subject/visit

    :parameter processed_subject_path:
    :parameter modality_name: string identifying the modality of the nifti file
    :return: path to the "top-most" .dcm file returned by the shell command 'ls -1 head'
    """

    dicom_root_dir, subj_id, visit_id, pipeline_version = get_searchable_parts_from_processed_path(processed_subject_path)

    if os.path.exists(dicom_root_dir):

        acquisitions = os.listdir(dicom_root_dir)
        print 'Folders found within dicom root directory for this subject: \n%s' % acquisitions

        for folder in acquisitions:
            if modality_name in folder:
                # take the first match you get... for now that should be fine / stable?
                dcm_file = submit_command('ls %s/*.dcm | head -1' % folder)

                return path.abspath(dcm_file)

    else:
        return None

def get_dicom_path_from_nifti_info(dicom_root_dir, modality_name):
    """
    Uses another helper function to find a dicom path for a given nifti modality and subject/visit

    :parameter dicom_root_dir:
    :parameter modality_name: string identifying the modality of the nifti file
    :return: path to the .dcm file
    """

    if os.path.exists(dicom_root_dir):

        dicoms = os.listdir(dicom_root_dir)
#        print 'Folders found within dicom root directory for this subject: \n%s' % acquisitions

        for dicom in dicoms:
            if modality_name in dicom:
                return path.join(dicom_root_dir, dicom)

    else:
        return None



def get_searchable_parts_from_processed_path(path_to_processed_subject_data):
    """
    Takes only the path to the processed_subject_directory, handles trailing slashes and finds /dicom, if exists.

    :parameter path_to_processed_subject_data:
    :return: (tuple) dicom root, subjid, visit_id, pipeline_version
    """

    sub_root = handle_trailing_slash(path_to_processed_subject_data)

    path_parts = sub_root.split('/')

    pipeline_version = path_parts[-2]

    subj_id = path_parts[-1]

    visit_id = path_parts[-3]

    if 'release' not in pipeline_version.lower():
        update_user('Not a HCP_generic-like structure with final directory=subject_code...Using Old-School '
                    'Structure...')
        pipeline_version = path_parts[-1]
        visit_id = path_parts[-2]
        subj_id = path_parts[-3]

    print '\nSubjID and Visit: %s %s: \n\n' % (subj_id, visit_id)

    update_user('pipeline_version is: %s\n' % pipeline_version)

    date_section = path.basename(visit_id).split('_')[0]

    year = date_section[:4]

    month = date_section[4:6]

    day = date_section[6:8]

    update_user('year month day == %s %s %s' % (year, month, day))

    dicom_root = '/dicom/%(year)s/%(month)s/%(subject_ID)s/%(day)s_%(subj_id_no_dash)s/' % {

          'year'            : year,
          'month'           : month,
          'day'             : day,
          'subject_ID'      : subj_id,
          'subj_id_no_dash' : subj_id[:-2]
    }

    update_user('dicom root is: \n%s' % dicom_root)

    if path.exists(dicom_root):
        print os.listdir(dicom_root)[0]
    else:
        update_user('Unable to locate dicom root on the airc...\ncheck: %s' % dicom_root)

    return dicom_root, subj_id, visit_id, pipeline_version

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


def make_img_list(path_to_dir):
    """
    Takes path to any directory, and returns a list of image_paths for all .gif an .png found via listdir()

    :parameter path_to_dir: directory where you think there will be *.gif or *.png and you don't care which / how many
    :return: list of image paths
    """

    images = []
    for image in os.listdir(path_to_dir):
        if image.endswith('.png') or image.endswith('gif'):
            images.append(path.join(image))

    return images

