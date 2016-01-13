#!/usr/bin/env python
"""
__author__ = 'Shannon Buckley', 12/27/15
"""

import os
import argparse
from os import path
import logging
from datetime import datetime
import glob
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


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

# for example
project_root = os.path.join('/remote_home/bucklesh/Projects/ExecutiveSummary/TestData/')


def get_subject_code(path_to_data_file):

    filename = os.path.basename(path_to_data_file)

    subject_code = filename.split('_')[0]

    return subject_code


def rename_image(img_path):
    """:arg img_path should be full-path to any image file
        :returns renamed, full-path to new image filename"""

    filename, file_extension = path.splitext(path.basename(img_path))

    if filename in images_dict.keys():

        new_filename = images_dict[filename]

        new_file_path = path.join(path.dirname(img_path), new_filename, file_extension)

        os.rename(img_path, new_file_path)

        return new_file_path


def get_epi_info(path_to_raw):
    """:arg path to raw EPI data storage
        :returns dict of params for each EPI acquisition with format:
            REST#: (x,y,z,TE,TR,etc)"""

    # need this?
    subcode = get_subject_code(path_to_raw)

    epi_info = {}

    epi_files = []

    raw_files = os.listdir(path_to_raw)

    # for example...
    rs_pattern = '%(code)s_REST%(acq_num)d' % {'code': subcode, 'acq_num': series_num}

    for file in raw_files:
        if file == glob.glob1(path_to_raw, rs_pattern):
            epi_files.append(file)

    return epi_info


def rename_structural(path_to_summary):

    structural_imgs = ['temp_13', 'temp_3', 'temp_9', 'temp_14', 'temp_4', 'temp_10']

    new_imgs = []

    for img_label in structural_imgs:

        filename = os.path.join(path_to_summary, img_label, '.png')

        new_file = rename_image(filename)

        new_imgs.append(new_file)

    return new_imgs


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


def main():

    date_stamp = "{:%Y_%m_%d}".format(datetime.now())

    _log = logging.getLogger('my_log.log')

    _log.info('Starting Up...')

    parser = argparse.ArgumentParser(description='Maker of Image Summaries.')

    parser.add_argument('-l', '--list', action="store", dest='file_list', help="Provide a full path to a data folder.")
    parser.add_argument('-v', '--verbose', dest="verbose", action="store_true", help="Tell me all about it.")

    args = parser.parse_args()

    if args.verbose:
        _log.setLevel(logging.DEBUG)
    else:
        _log.setLevel(logging.INFO)


if __name__ == '__main__':

    main()

