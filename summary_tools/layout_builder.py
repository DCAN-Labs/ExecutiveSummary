#!/usr/bin/env python
"""
Call this program with -s, pointing to a subject-summary_tools path, to build the Executive Summary for that subject's
processed data.
-o for optional output_directory; (default =
/group_shares/FAIR_LAB2/Projects/FAIR_users/Shannon/QC_todo/<date>/subjID_visit)

__author__ = 'Shannon Buckley', 2/20/16
"""

import os
from os import path
import argparse
import image_summary
from image_summary import _logger
import glob
import shutil
import logging
import sys
from helpers import shenanigans

PROG = 'Layout Builder'
VERSION = '1.4.0'
LAST_MOD = '8-1-16'

program_desc = """%(prog)s v%(ver)s:
Builds the layout for the Executive Summary by writing-out chunks of html with some help from image_summary methods.
Use -s /path/to/subjectfolder/with/summary_subfolder to launch and build a summary page.
Has embedded css & jquery elements.
""" % {'prog': PROG, 'ver': VERSION}


def get_parser():

    parser = argparse.ArgumentParser(description=program_desc, prog=PROG, version=VERSION)

    parser.add_argument('-s', '--subject_path', dest='subject_path', action='append',
                        help='''Expects path to a subject-level directory of processed data, which should have a
                        'summary' folder within (e.g./remote_home/bucklesh/Projects/TestData/ABCDPILOT_MSC02/)''')

    parser.add_argument('-o', '--output_path', dest='output_path', action='store',
                        help='''Expects path to a folder you can write to in order to copy final outputs there. Final
                        goodies will be inside a directory on the output_path: date_stamp/SUBJ_ID.''')

    parser.add_argument('-l', '--list_file', dest='list_file', required=False, help="""Optional: path to file containing
    list of processed-subject-paths, e.g. /scratch/HCP/processed/ASD-blah/subjCode/VisitID/subjCode .""")

    parser.add_argument('--verbose', dest="verbose", action="store_true", help="Tell me all about it.")

    parser.add_argument('-vv', '--very_verbose', dest="very_verbose", action="store_true", help="Tell me all about it.")

    return parser

# HTML BUILDING BLOCKS
html_header = """<!DOCTYPE html>
<html lang = "en">
    <head>
        <meta charset = "utf-8">
        <title>Executive Summary: CODE_VISIT</title>
        <style type="text/css">.epi,.grayords,.params{position:relative}.header,button,table,td{text-align:center}body{background-color:#c3c4c3}span{font-size:10px}img{border-radius:5px}.header{font-family:Garamond;margin-top:25px;margin-bottom:15px}table,td{border:1px dashed #70b8ff}.epi td,.params td,.top-left-panel table,td{border:none}.top-left-panel{float:left;width:50%}.top-left-panel img{width:250px;height:200px}.epi{float:right}.epi img{width:175px;height:150px}.raw_rest_img img {width: 300px;height: 110px}.params{float:left;width:40%}.params th{border-bottom:1px #70b8ff solid}.params .column-names{border-bottom:1px #00f solid;font-weight:700}.grayords{float:right}.grayords img{width:350px;height:300px}.out-of-range{color:red}button{cursor:pointer;display:inline-block;height:20px;width:70px;font-family:arial;font-weight:700;margin-top:2px}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>CODE_VISIT</h1>
            <p>VERSION</p>
            </div>
        </div>"""

param_table_html_header = """
        <div class="bottom-row">
            <div class="params">
                <table id="param_table">
                    <thead>
                        <th colspan="8">
                            Acquisition Parameters
                        </th>
                    </thead>
                    <tbody>
                        <tr class="column-names">
                            <td>Modality</td>
                            <td>x <span>(mm)</span></td>
                            <td>y <span>(mm)</span></td>
                            <td>z <span>(mm)</span></td>
                            <td>TE <span>(ms)</span></td>
                            <td>TR <span>(ms)</span></td>
                            <td>Frames <span>(n)</span></td>
                            <td>TI <span>(ms)</span></td>
                        </tr>"""

param_table_footer = """
                    </tbody>
                </table>
            </div>"""

epi_panel_header = """
            <div class="epi">
                <table id="epi">
                    <thead>
                        <th colspan="4">
                            Resting State Data
                        </th>
                    </thead>
                    <tbody>"""

epi_panel_footer = """
                    </tbody>
                </table>
            </div>
        </div>"""

html_footer = """
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
        <script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.9.1/jquery-ui.min.js"></script>
        <script>$(document).ready(function(){$("img[src*=SBRef]").width(300).height(110),$('img').filter('.raw_rest_img').width(300).height(110),$(".t1_tr").each(function(t,a){"2400.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t1_te").each(function(t,a){"4.97"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t1_x").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t1_y").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t1_z").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_frames").each(function(t,a){"120"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_x").each(function(t,a){"3.8"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_y").each(function(t,a){"3.8"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_z").each(function(t,a){"3.8"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_tr").each(function(t,a){"2100.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_te").each(function(t,a){"5.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_x").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_y").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_z").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_tr").each(function(t,a){"3200.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_te").each(function(t,a){"4.97"!=$(a).text()&&$(a).addClass("out-of-range")}),$("div.params").draggable(),$("div.grayords").draggable(),$("div.epi").draggable()});
        </script>
    </body>
</html>
"""


def write_html(template, dest_dir, title="executive_summary.html"):
    """
    Takes an html template string and a destination, then writes it out to a default title.

    :parameter: template: path to html template
    :parameter: dest_dir: output path for final .html file
    :parameter: title: string to apply to output
    :return: None
    """

    if not title.endswith('.html'):
        title += '.html'

    try:
        f = open(path.join(dest_dir, title), 'w')
        f.writelines(template)
        f.close()
    except IOError:
        print 'cannot write there for some reason...'


def write_structural_panel(list_of_image_paths):
    """
    Builds a panel of orthogonally sliced T1 and T2 images with pial and white matter surface overlays from Freesurfer.

    :parameter: list_of_image_paths: list of 6 image paths for the structural image panel
    :return: string of html containing a div row with an images table
    """

    if len(list_of_image_paths) < 6:
        _logger.error('not enough structural images!')
        return

    structural_html_panel = """
    <div class="top-row">
            <div class="structural">
                <table class="top-left-panel">
                    <thead>
                        <th colspan="3">
                            Structural Segmentation
                        </th>
                    </thead>
                <tbody>
                    <tr>
                        <td><a href=img/%(T1-left)s target="_blank"><img src=img/%(T1-left)s></a></td>
                        <td><a href=img/%(T1-middle)s target="_blank"><img src=img/%(T1-middle)s></a></td>
                        <td><a href=img/%(T1-right)s target="_blank"><img src=img/%(T1-right)s></a></td>
                    </tr>
                    <tr>
                        <td><a href=img/%(T2-left)s target="_blank"><img src=img/%(T2-left)s></a></td>
                        <td><a href=img/%(T2-middle)s target="_blank"><img src=img/%(T2-middle)s></a></td>
                        <td><a href=img/%(T2-right)s target="_blank"><img src=img/%(T2-right)s></a></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>""" % {'T1-left': list_of_image_paths[0],
                 'T1-middle': list_of_image_paths[1],
                 'T1-right': list_of_image_paths[2],
                 'T2-left': list_of_image_paths[3],
                 'T2-middle': list_of_image_paths[4],
                 'T2-right': list_of_image_paths[5]
                 }

    return structural_html_panel


def edit_html_chunk(html_string, thing_to_find, thing_that_replaces_it):
    """
    Takes some html string, does a find/replace on it.

    :parameter: html_string: any string, really
    :parameter: thing_to_find: any string
    :parameter: thing_that_replaces_it: replacement string
    :return: new string with replacement
    """

    new_html_string = html_string.replace(thing_to_find, thing_that_replaces_it)

    return new_html_string


def write_param_table_row(list_of_data):
    """
    Takes a list of data and fills in one row in the parameter table per datum

    :parameter: list_of_data: list of data with 8 elements
    :return: param_table_row with specific metrics (8 columns)
    """

    if len(list_of_data) != 8 or list_of_data[5] == '':
        _logger.error('list of data is incomplete:\n%s' % list_of_data)
        return

    param_table_html_row = """
                        <tr class="%(class_prefix)s_data">
                            <td>%(modality)s</td>
                            <td id="%(class_prefix)s_x" class="%(class_prefix)s_x">%(x_dim)s</td>
                            <td id="%(class_prefix)s_y" class="%(class_prefix)s_y">%(y_dim)s</td>
                            <td id="%(class_prefix)s_z" class="%(class_prefix)s_z">%(z_dim)s</td>
                            <td id="%(class_prefix)s_te" class="te">%(te)s</td>
                            <td id="%(class_prefix)s_tr">%(tr)s</td>
                            <td id="%(class_prefix)s_frames" class="%(class_prefix)s_frames">%(frames)s</td>
                            <td id="%(class_prefix)s_ti">%(ti)s</td>
                        </tr>""" % {'modality': list_of_data[0],
                                    'class_prefix': list_of_data[0].lower(),
                                    'x_dim': list_of_data[1],
                                    'y_dim': list_of_data[2],
                                    'z_dim': list_of_data[3],
                                    'te': list_of_data[4],
                                    'tr': list_of_data[5],
                                    'frames': list_of_data[6],
                                    'ti': list_of_data[7]
                                    }

    return param_table_html_row


def write_epi_panel_row(list_of_img_paths):
    """
    Takes a list of image paths and builds one row of epi_images for the panel.

    :parameter: list_of_img_paths: list of paths
    :return: one row of an html table, <tr> to </tr> with epi-images for a given series
    """

    if len(list_of_img_paths) < 4:
        _logger.error('insufficient files to build an epi-panel row!\nCheck your list: %s ' % list_of_img_paths)
        print 'do not have a full row (4 images) of epi-data for this subject'
        return

    epi_panel_row = """
                    <tr>
                        <td><a href="%(rest_in_t1)s" target="_blank"><img src="%(rest_in_t1)s"></a></td>
                        <td><a href="%(t1_in_rest)s" target="_blank"><img src="%(t1_in_rest)s"></a></td>
                        <td><a href="%(sb_ref)s" target="_blank"><img src="%(sb_ref)s"></a></td>
                        <td><a href="%(rest_nonlin_norm)s" target="_blank"><img src="%(rest_nonlin_norm)s"
                            class="raw_rest_img"></a></td>
                    </tr>""" % {'rest_in_t1'        : list_of_img_paths[0],
                                't1_in_rest'        : list_of_img_paths[1],
                                'sb_ref'            : list_of_img_paths[2],
                                'rest_nonlin_norm'  : list_of_img_paths[3]}

    return epi_panel_row


def make_epi_panel(epi_rows_list, header=epi_panel_header, footer=epi_panel_footer):
    """
    Takes a list of panel rows (html_strings), a header and footer to build the full epi-panel.

    :parameter: epi_rows_list: list of data rows (strings)
    :parameter: header: div section opener
    :parameter: footer: dev section closer
    :return: html string for the whole epi-panel div (one row of images per REST)
    """

    epi_panel_html = header

    for row in epi_rows_list:
        epi_panel_html += row
    epi_panel_html += footer

    return epi_panel_html


def write_dvars_panel(dvars_input_path='img/DVARS_and_FD_CONCA.png'):
    """
    Takes a path to a specific image and writes up a div for it

    :parameter: dvars_input_path: path to DVARS image.png expected
    :return: div section string for DVARS
    """

    dvars_panel_html_string = """
            <div class="grayords">
                <table class="grayords">
                <thead>
                    <th colspan="3">
                        Resting State Grayordinates Plot
                    </th>
                </thead>
                <tbody>
                    <tr>
                        <td><a href="%(dvars_path)s" target="_blank">
                                <img src="%(dvars_path)s"></a>
                        </td>
                    </tr>
                    </tbody>
                </table>
            </div>""" % {'dvars_path' : dvars_input_path}

    return dvars_panel_html_string


def append_html_with_chunk(existing_html, string_to_insert):
    """
    Takes some html string, appends a chunk to it, returns the new chunk+extension.

    :parameter: existing_html: string
    :parameter: string_to_insert: another string
    :return: appended string
    """

    new_html_string = existing_html + string_to_insert

    return new_html_string


def copy_images(src_dir, list_of_images, dst_dir='./img/'):
    """
    Takes a source dir and a list of images, copies them to a default destination ./img.

    :parameter: src_dir: copy from path
    :parameter: list_of_images: list of image names to copy (full paths not expected)
    :parameter: dst_dir: copy to  path
    :return: None
    """

    if type(list_of_images) == str:
        img_path = path.join(src_dir, list_of_images)
        shutil.copyfile(img_path, dst_dir)

    elif type(list_of_images) == list:
        for image in list_of_images:
            img_path = path.join(src_dir, image)
            shutil.copyfile(img_path, path.join(dst_dir, image))


def main():

    parser = get_parser()

    args = parser.parse_args()

    if args.verbose:
        _logger.setLevel(logging.INFO)
    elif args.very_verbose:
        _logger.setLevel(logging.DEBUG)
    else:
        _logger.setLevel(logging.ERROR)

    if args.list_file:

        file_we_read_in = path.join(args.list_file)

        if not path.exists(file_we_read_in) or not file_we_read_in.endswith('.txt'):
            shenanigans.update_user('List FILE (.txt) does not exist, please verify your path to: \n%s' %
                                    file_we_read_in)
            sys.exit()

        if path.exists(file_we_read_in):

            paths_to_process = shenanigans.read_list_file(file_we_read_in)

            # print paths_to_process

            for path_to_proc in paths_to_process:

                path_to_proc = path_to_proc.strip('\n')

                command = 'python %s -s %s' % (sys.argv[0], path.join(path_to_proc))

                shenanigans.submit_command(command)

    if args.subject_path:

        for sub in args.subject_path:

            sub_root = path.join(sub)

            if path.exists(sub_root):

                sub_root = shenanigans.handle_trailing_slash(sub_root)

                # ------------------------- > GATHER BASIC INFO < ------------------------- #

                summary_path, data_path = image_summary.get_paths(sub_root)

                dicom_root, subj_id, visit_id, pipeline_version = \
                    shenanigans.get_searchable_parts_from_processed_path(sub_root)

                # path_parts = sub_root.split('/')
                #
                #
                #
                # subj_id = path_parts[-1]
                #
                # pipeline_version = path_parts[-2]
                #
                # visit_id = path_parts[-3]

                if 'release' not in pipeline_version:
                    print '\nthis may or may not workout if this is not a standard HCP_release! *fingers crossed*'

                print '\npipeline_version is: %s\n' % pipeline_version

                shenanigans.update_user('SubjID and Visit: \n%s %s\nPipeline: %s' % (subj_id, visit_id,
                                                                                     pipeline_version))

                date = image_summary.date_stamp

                # ------------------------- > WRITE OUT SUMMARY REPORT < ------------------------- #
                with open(path.join(sub_root, 'Summary_Report.txt'), 'w') as f:

                    info = '''
                            Executive Summary ran on %s
                            pipeline %s was detected
                            Subject Path provided: \n%s
                            Subject Code: %s
                            Visti_ID: %s
                            Args: \n%s
                            ''' % (date, pipeline_version, sub_root, subj_id, visit_id, args)

                    f.write(info)
                    f.close()

            else:

                print '\nNo subject directory found within %s \nexiting...' % sub
                _logger.error('\nNo subject directory within %s \nexiting...' % sub)

                continue

            # --------------------------------- > SETUP PATHS < --------------------------------- #
            if path.exists(summary_path):

                img_out_path = path.join(sub_root, 'summary', 'img')
                img_in_path = summary_path
                subject_code_folder = path.join(summary_path, subj_id + '_' + visit_id)

            else:

                print '\nMake sure a "summary" folder exists or this will not work...\n\tcheck in here: %s' % sub_root
                _logger.error('\nno Summary folder exists within %s\n' % sub_root)

                continue
            # ------------------------- > MAKE /img or quit ... CHECK IMAGES < ------------------------- #
            if not path.exists(img_out_path):

                try:

                    os.makedirs(img_out_path)

                except OSError:

                    print '\nCheck permissions to write to that path? \npath: %s' % summary_path
                    _logger.error('cannot make /img within /summary... permissions? \nPath: %s' % summary_path)

                    return

            try:
                gifs = [gif for gif in os.listdir(img_in_path) if gif.endswith('gif')]

                if len(gifs) == 0:

                    _logger.error('no .gifs in summary folder')
                    print '\nNo summary .gifs were found! There should be some .gifs and I do not make those! '\
                        'Check to make sure FNL_preproc has been ran? '

                    return

                else:

                    copy_images(img_in_path, gifs, img_out_path)

                    data = image_summary.get_list_of_data(data_path)

                    _logger.debug('data are: %s' % data)

            except OSError:

                    print '\n\tUnable to locate image sources...'

                    return

            # ------------------------- > Make lists of paths to be used in the epi-panel < -------------------------- #
            real_data = []
            epi_in_t1_gifs = sorted([path.join('./img', path.basename(gif)) for gif in gifs if '_in_t1.gif' in gif and 'atlas' not in gif])

            t1_in_epi_gifs = sorted([path.join('./img', path.basename(gif)) for gif in gifs if '_t1_in_REST' in gif])

            # setup an output directory
            if not path.exists(subject_code_folder):

                os.makedirs(subject_code_folder)

            # ------------------------- > Check list of epi-data to ensure even numbers of files... < ---------------- #
            # TODO: improve this section with a more specific test

            if len(data['epi-data']) % 2 != 0:  # we should have at least 1 raw REST and 1 SBRef per subject (pairs)

                _logger.warning('odd number of epi files were found...')
                print '\nLooking for SBRef images...\n'

                # locate an alternative source for SBRef images -> MNINonLinear/Results/REST?

                # alt_sbref_path = path.join(sub_root, 'MNINonLinear', 'Results')
                # pattern = alt_sbref_path + '/REST?/REST?_SBRef.nii.gz'
                # more_epi = glob.glob(pattern)
                #
                # for sbref in more_epi:
                #     data['epi-data'].append(sbref)

                alternate_sbref_path = path.join(sub_root)
                sbref_pattern = alternate_sbref_path + '/REST?/Scout_orig.nii.gz'

                more_sbref = glob.glob(sbref_pattern)
                # print 'found additional SBRef files: %s' % more_sbref

                for sbref in more_sbref:
                    data['epi-data'].append(sbref)


            # ------------------------- > SLICING UP IMAGES FOR EPI DATA LIST < ------------------------- #

            for list_entry in data['epi-data']:

                info = image_summary.get_subject_info(list_entry)

                # get modality / series so we can know how to slice & label ...
                modality, series = info[1], info[2]
                print '\nPROCESSING subject_code: %s, modality: %s ' % (subj_id, modality)
                print 'slicing images for: \n%s' % list_entry

                if 'REST' in modality and 'SBRef' not in modality:

                    image_summary.slice_list_of_data([list_entry], subject_code=subj_id, modality=modality,
                                                     dest_dir=img_out_path, also_xyz=True)

                elif 'SBRef' in modality and 'REST' in modality:

                    image_summary.slice_image_to_ortho_row(list_entry, path.join(img_out_path, '%s.png' % modality))

                elif 'SBRef' in modality:

                    image_summary.slice_image_to_ortho_row(list_entry, path.join(img_out_path, '%s%s.png' % (modality,
                                                                                                             series)))

            # ITERATE through data dictionary keys, sort the list (value), then iterate through each list for params
            for list_entry in data.values():

                list_entry = sorted(list_entry)

                for item in list_entry:

                    information = image_summary.get_subject_info(item)

                    modality, series = information[1], information[2]

                    dicom_for_te_grabber = shenanigans.get_airc_dicom_path_from_nifti_info(sub_root, modality)

                    nifti_te = shenanigans.grab_te_from_dicom(dicom_for_te_grabber)

                    print '\nTE for this file was: %s\n' % nifti_te

                    print '\nadding %s to list of data, for which we need parameters...\n' % item

                    _logger.debug('data_list is: %s' % data)

                    params_row = image_summary.get_nii_info(item)

                    alt_params_row = shenanigans.get_dcm_info(dicom_for_te_grabber, modality)
                    print '\nTESTING PARAMS GETTER.....\n'
                    print '\nOld Way params_row = %s\n' % params_row
                    print '\nNew Way alt_params_row = %s\n' % alt_params_row

                    real_data.append(params_row)

            # -------------------------> START TO BUILD THE LAYOUT <------------------------- #

            head = html_header

            html_params_panel = param_table_html_header

            # BUILD PARAM PANEL

            for data_row in real_data:
                html_params_panel += write_param_table_row(data_row)

            html_params_panel += param_table_footer

            # BUILD & WRITE THE STRUCTURAL PANEL

            structural_img_labels = ['T1-Sagittal-Insula-FrontoTemporal.png',
                                     'T1-Axial-BasalGangila-Putamen.png',
                                     'T1-Coronal-Caudate-Amygdala.png',
                                     'T2-Sagittal-Insula-FrontoTemporal.png',
                                     'T2-Axial-BasalGangila-Putamen.png',
                                     'T2-Coronal-Caudate-Amygdala.png'
                                     ]

            body = write_structural_panel(structural_img_labels)

            # APPEND WITH PARAMS PANEL

            new_body = body + html_params_panel

            pngs = [png for png in os.listdir(img_out_path) if png.endswith('png')]  # does not include DVARS

            # BUILD THE LISTS NEEDED FOR EPI-PANEL

            raw_rest_img_pattern = path.join(img_out_path, 'REST?.png')
            raw_rest_img_list = glob.glob(raw_rest_img_pattern)

            rest_raw_paths = sorted([path.join('./img', path.basename(img)) for img in raw_rest_img_list])
            # print rest_raw_paths
            sb_ref_paths = sorted([path.join('./img', img) for img in pngs if 'SBRef' in img])
            # print sb_ref_paths

            # INITIALIZE AND BUILD NEW LIST WITH MATCHED SERIES CODES FOR EACH EPI-TYPE
            print '\nAssembling epi-images to build panel...'
            epi_rows = []

            num_epi_gifs = len(t1_in_epi_gifs)

            if num_epi_gifs != len(epi_in_t1_gifs):
                _logger.error('incorrect number of gifs !\nepi_in_t1 count: %s\nt1_in_epi_count: %s' %(len(epi_in_t1_gifs), num_epi_gifs))
                print 'ack, something went wrong while trying to assemble epi-data! exiting...'
                continue
            elif num_epi_gifs != len(rest_raw_paths):
                _logger.error('incorrect number of raw epi files!\nepi_rows: %s\nnum_epi_files: %s' %(len(rest_raw_paths), num_epi_gifs))
                print 'ack, something went wrong while trying to assemble epi-data! exiting...'
                continue
            elif num_epi_gifs != len(sb_ref_paths):
                _logger.error('incorrect number of sb_ref files!\nepi_rows: %s\nnum_epi_files: %s' %(len(sb_ref_paths), num_epi_gifs))
                print 'ack, something went wrong while trying to assemble epi-data! exiting...'
                continue
            else:

                # APPEND NEW EPI-PANEL SECTIONS
                newer_body = new_body + epi_panel_header
                for i in range(0, num_epi_gifs):
                    epi_rows.append(epi_in_t1_gifs.pop(0))
                    epi_rows.append(t1_in_epi_gifs.pop(0))
                    epi_rows.append(sb_ref_paths.pop(0))
                    epi_rows.append(rest_raw_paths.pop(0))

                    newer_body += write_epi_panel_row(epi_rows[:4])
                    _logger.debug('\nepi_rows were: %s' % epi_rows)
                    epi_rows = []

            # COMPLETE EPI PANEls

            newer_body += epi_panel_footer

            _logger.debug('newer_body is : %s' % newer_body)

            shutil.copy(path.join(img_in_path, 'DVARS_and_FD_CONCA.png'), img_out_path)
            dvars_path = path.join(img_out_path, 'DVARS_and_FD_CONCA.png')

            try:

                copy_images(img_in_path, structural_img_labels, img_out_path)  # out: /summary/img/<blah>

            except IOError:

                _logger.warning('\nUnable to locate some structural images. Do they exist?')
                print '\nMake sure you have all 6 structural .png and DVARS available for this subject: %s_%s' % (
                    subj_id, visit_id)

                print '\nExpected path to required images: %s' % img_in_path

            # FILL-IN THE CODE / VERSION INFO
            new_html_header = edit_html_chunk(head, 'CODE_VISIT', '%s_%s' % (subj_id, visit_id))

            new_html_header = edit_html_chunk(new_html_header, 'VERSION', 'Executive Summary_v' + VERSION)

            # ASSEMBLE THE WHOLE DOC, THEN WRITE IT!

            html_doc = new_html_header + newer_body + write_dvars_panel(path.join('./img', path.basename(dvars_path)))

            html_doc += html_footer

            write_html(html_doc, summary_path, title='executive_summary_%s_%s.html' % (subj_id, visit_id))

            # -------------------------> END LAYOUT <------------------------- #

            # -------------------------> PREPARE QC PACKET <------------------------- #
            move_cmd = "mv %(img_in_path)s/*.html %(sub_code_folder)s; mv %(img_in_path)s/img %(sub_code_folder)s" % {
                        'sub_code_folder'  : subject_code_folder,
                        'img_in_path'      : img_in_path}

            image_summary.submit_command(move_cmd)

            if args.output_path:

                user_out_path = path.join(args.output_path)

                if path.exists(user_out_path):

                    print 'found path: %s, using this to copy for QC' % user_out_path

                    qc_folder_out = path.join(user_out_path, image_summary.date_stamp, subj_id + '_' + visit_id)

                    print '\nFind your images here: \n\t%s' % qc_folder_out

            else:

                qc_folder_out = path.join('/group_shares/FAIR_LAB2/Projects/FAIR_users/Shannon/QC_todo/%s/%s' %
                                          (image_summary.date_stamp, subj_id + '_' + visit_id))

                print '\nusing default output path to copy images for QC: \n%s' % qc_folder_out

            if not path.exists(qc_folder_out):

                print '\ncopying to QC_folder\n\n'

                shutil.copytree(subject_code_folder, qc_folder_out)  # only works if the des_dir doesn't already exist

    else:
        print '\nNo subject path provided!'
        _logger.error('No subject path provided!')

if __name__ == '__main__':

    main()

    print '\nall done!'
