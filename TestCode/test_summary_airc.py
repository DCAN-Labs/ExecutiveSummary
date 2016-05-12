#!/usr/bin/env python
"""
__author__ = 'Shannon Buckley', 12/27/15

testing the dicom-info grabber, mostly.
"""

from summary_tools import image_summary
import os
from helpers import shenanigans
import re

test_sub_path = '/remote_home/bucklesh/Projects/TestData/ABCDPILOT_MSC02'

out_path = os.path.join(test_sub_path, 'summary')

if not os.path.exists(out_path):
    print 'no summary folder!'

image_summary.get_paths(test_sub_path)

param_table = os.path.join(out_path + 'Params.csv')

# write out the first row of our data rows to setup column headers
data_rows = [['Modality', 'x', 'y', 'z', 'TR', 'TE', 'frames', 'TI']]

image_summary.write_csv(data_rows, param_table)


more_data = image_summary.get_list_of_data(os.path.dirname(
        '/remote_home/bucklesh/Projects/TestData/unprocessed/NIFTI/'))


for list_entry in more_data:
    if len(list_entry) > 0:
        for item in list_entry:
            data_rows.append(image_summary.get_nii_info(item))

# DICOM tests

dicom_path = '/dicom/2015/12/11378_013_11378_013/04_1310/007-PD_fl3D/1.3.12.2.1107.5.2.34.18913.2015120413391664710789251.dcm'

even_more_data = shenanigans.get_dcm_info(dicom_path, 'PD-Flair')

print even_more_data

data_rows.append(even_more_data)

image_summary.write_csv(data_rows, param_table)
###############

print '#' * 24 + '\nTESTING SHENANIGANS\n' + '#' * 24
print 'TESTING get_searchable_parts_from_processed_path\n' + '#' * 24
shenanigans.get_searchable_parts_from_processed_path('/Users/st_buckls/imageprocessing/Projects/PPMI/088m00_PPMI/20121104_PPMI'
                                          '/pipeline')
print '\nDONE\n' + '#' * 24

t1_pattern = r'\w+_T1[\w.]+'
t1_matches = re.findall(t1_pattern, ' '.join(os.listdir(
    '/Users/st_buckls/imageprocessing/Projects/PPMI/088m00_PPMI/20121104_PPMI'
                                            '/pipeline')))

rest_pattern = r'\w+_REST\d_[\w.]+'

epi_matches = re.findall(rest_pattern, ' '.join(os.listdir(
    '/Users/st_buckls/imageprocessing/Projects/PPMI/088m00_PPMI/20121104_PPMI'
                                            '/pipeline')))

print '\ndata: ' + ' '.join(os.listdir(
    '/Users/st_buckls/imageprocessing/Projects/PPMI/088m00_PPMI/20121104_PPMI'
                                            '/pipeline'))

if t1_matches:
    print '\nt1 matches: \n%s' % t1_matches

if epi_matches:
    print '\nrest matches: \n%s' % epi_matches