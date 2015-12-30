#!/usr/local/bin/python
"""
__author__ = 'Shannon Buckley', 12/27/15
"""

import os
import argparse
from os import path
import logging


_log = logging.getLogger('my_log.log')

_log.info('Starting Up...')

images_dict = {'temp_1' : 'T1-Axial-InferiorTemporal-Cerebellum',
               'temp_2' : 'T2-Axial-InferiorTemporal-Cerebellum',
               'temp_13': 'T1-Coronal-Hippocampus',
               'temp_14': 'T2-Coronal-Hippocampus',
               'temp_15': 'T1-Sagittal-CorpusCallosum',
               'temp_16': 'T2-Coronal-CorpusCallosum',
               }




def rename_image(img_path):

    filename, file_extension = path.splitext(path.basename(img_path))

    if filename in images_dict.keys():

        new_filename = images_dict[filename]

        new_file_path = path.join(path.dirname(img_path), new_filename, file_extension)

        os.rename(img_path, new_file_path)


def get_png_count(path):

    

def rename_structural_images(path):

    if len(os.listdir(path)) < 6:
        print 'Structural summary requires 6 images.'
        quit()



def main():

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

    rename_image()

