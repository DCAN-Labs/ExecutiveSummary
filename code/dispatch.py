#!/usr/bin/env python
"""
__author__ = 'Shannon Buckley', 2/12/16
"""

import os, sys
from os import path
import image_summary
import logging
from datetime import datetime

PROG = 'Dispatcher'

VERSION = '0.0.0'

date_stamp = "{:%Y_%m_%d_%H:%M:%S}".format(datetime.now())

if not path.exists(path.join(os.getcwd(), 'logs')):
    os.makedirs('logs')

logfile = os.path.join(os.getcwd(), 'logs', ('%s_Log-%s.log' % (PROG, date_stamp)))

logging.basicConfig(filename=logfile,
                    level=logging.DEBUG,
                    )

log = logging.getLogger('%(prog)s_v%(ver)s' % {'prog': PROG, 'ver': VERSION, 'date': "{:%Y_%m_%d_%H:%M:%S}".format(datetime.now())})

# log.info('ran on %s\n' % (date_stamp))

nifti_file = path.join('/Users/st_buckls/imageprocessing/Projects/PPMI/data/PPMI/rPPMI_088_S_3551m00_i226427_REST1_brain.nii')
nifti_gz_file = path.join('/Users/st_buckls/imageprocessing/Projects/PPMI/data/PPMI/rPPMI_088_S_3551m00_i226427_REST2_brain.nii.gz')

log.info('retrieving info from nifti file: %s' % nifti_file)
nii_info = image_summary.get_nii_info(nifti_file)

log.info('calling image_summary with nifti_file...')

#image_summary.submit_command('python image_summary.py -v -n %s' % nifti_file)

log.info('setting up image slicer...')
img_out_path = os.path.join(os.getcwd(), 'img')

if not os.path.exists(img_out_path):
    os.makedirs(img_out_path)

T2_slices = {
    'x': 55,
    'y': 115,
    'z': 145
}

epi_slices = {
    'x': 55,
    'y': 135,
    'z': 130
}

if 'REST' in nii_info[0]:
    slices_dict = epi_slices
elif 'T2' or 'T1' in nii_info[0]:
    slices_dict = T2_slices

log.info('slicing...')
image_summary.super_slice_me(nifti_file, 'x', slices_dict['x'], os.path.join(img_out_path, '%s_x-%d.png' % (nii_info[0],
                                                                                                            slices_dict['x'])))
log.info('dicing...')
image_summary.super_slice_me(nifti_file, 'y', slices_dict['y'], os.path.join(img_out_path, '%s_y-%d.png' % (nii_info[0],
                                                                                                            slices_dict['y'])))
image_summary.super_slice_me(nifti_file, 'z', slices_dict['z'], os.path.join(img_out_path, '%s_z-%d.png' % (nii_info[0],
                                                                                                           slices_dict['z'])))

# dicom_file = path.join('../in/0.dcm')
#
# dicom_info = image_summary.get_dcm_info(dicom_file, 'Unknown')
#
# if len(dicom_info) > 0:
#     image_summary.write_csv([dicom_info], path.join('../out/DicomParams.csv'))
#
#
# te = image_summary.grab_te_from_dicom(dicom_file)
#
list_of_data = image_summary.get_list_of_data(path.dirname(nifti_file))
gz_data = image_summary.get_list_of_data(nifti_gz_file)
print list_of_data
print gz_data
