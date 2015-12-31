#!/usr/bin/env python
"""
__author__ = 'Shannon Buckley', 12/27/15
"""

import os
import argparse
from os import path
import logging


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


def rename_image(img_path):

    filename, file_extension = path.splitext(path.basename(img_path))

    if filename in images_dict.keys():

        new_filename = images_dict[filename]

        new_file_path = path.join(path.dirname(img_path), new_filename, file_extension)

        os.rename(img_path, new_file_path)


def get_epi_count(path):

    pass
    

def rename_structural_images(path):

    if len(os.listdir(path)) < 6:
        print 'Structural summary requires 6 images.'
        quit()


def main():

    _log = logging.getLogger('my_log.log')

    _log.info('Starting Up...')

    parser = argparse.ArgumentParser(description='Maker of Image Summaries.')

    parser.add_argument('-l', '--list', action="store", dest='file_list', help="Provide a full path to a .txt with "
                                                                               "one column of participant codes.")
    parser.add_argument('-v', '--verbose', dest="verbose", action="store_true", help="Tell me all about it.")

    args = parser.parse_args()

    if args.verbose:
        _log.setLevel(logging.DEBUG)
    else:
        _log.setLevel(logging.INFO)


if __name__ == '__main__':

    main()

