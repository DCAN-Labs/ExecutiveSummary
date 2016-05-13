#!/usr/bin/env python
"""
__author__ = 'Shannon Buckley', 2/20/16

Call this program with -s, pointing to a subject-summary_tools path, to build the Executive Summary for that subject's
processed data.
"""

import os
from os import path
import argparse
import image_summary
from image_summary import _logger
import glob
import shutil

PROG = 'Layout Builder'
VERSION = '1.0.3'

LAST_MOD = '4-13-16'

program_desc = """%(prog)s v%(ver)s:
Builds the layout for the Executive Summary by writing-out chunks of html with some help from image_summary methods.
Use -s /path/to/subjectfolder/with/summary_subfolder to launch and build a summary page.
Has embedded css & jquery elements.
""" % {'prog': PROG, 'ver': VERSION}


def write_html(template, dest_dir, title="summary_out.html"):

    if not title.endswith('.html'):
        title += '.html'

    try:
        f = open(path.join(dest_dir, title), 'w')
        f.writelines(template)
        f.close()
    except IOError:
        print 'cannot write there for some reason...'

html_header = """<!DOCTYPE html>
<html lang = "en">
    <head>
        <meta charset = "utf-8">
        <title>Executive Summary: CODE</title>
        <style type="text/css">.epi,.grayords,.params{position:relative}.header,button,table,td{text-align:center}body{background-color:#c3c4c3}span{font-size:10px}img{border-radius:5px}.header{font-family:Garamond;margin-top:25px;margin-bottom:15px}table,td{border:1px dashed #70b8ff}.epi td,.params td,.top-left-panel table,td{border:none}.top-left-panel{float:left;width:50%}.top-left-panel img{width:250px;height:200px}.epi{float:right}.epi img{width:175px;height:150px}.raw_rest_img img {width: 300px;height: 110px}.params{float:left;width:40%}.params th{border-bottom:1px #70b8ff solid}.params .column-names{border-bottom:1px #00f solid;font-weight:700}.grayords{float:right}.grayords img{width:350px;height:300px}.out-of-range{color:red}button{cursor:pointer;display:inline-block;height:20px;width:70px;font-family:arial;font-weight:700;margin-top:2px}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>CODE</h1>
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


def get_subject_code(src_path):

    if path.exists(path.join(src_path)):
        path.relpath(src_path)

    subjID = ''

    return subjID


def copy_images(src_dir, list_of_images, dst_dir='./img/'):

    if type(list_of_images) == str:
        img_path = path.join(src_dir, list_of_images)
        shutil.copyfile(img_path, dst_dir)

    elif type(list_of_images) == list:
        for image in list_of_images:
            img_path = path.join(src_dir, image)
            shutil.copyfile(img_path, path.join(dst_dir, image))


def write_structural_panel(list_of_image_paths):
    """
    Builds a panel of orthogonally sliced T1 and T2 images with pial and white matter surface overlays from Freesurfer.

    :param list_of_image_paths:
    :return: string of html to create a table of images containing an
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

    new_html_string = html_string.replace(thing_to_find, thing_that_replaces_it)

    return new_html_string


def write_param_table_row(list_of_data):

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

    epi_panel_html = header

    for row in epi_rows_list:
        epi_panel_html += row
    epi_panel_html += footer

    return epi_panel_html


def write_dvars_panel(dvars_input_path='img/DVARS_and_FD_CONCA.png'):

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

    new_html_string = existing_html + string_to_insert

    return new_html_string


def main():

    parser = argparse.ArgumentParser(description=program_desc, prog=PROG)

    parser.add_argument('-s', '--subject_path', dest='subject_path', action='append',
                        help='''Expects path to a subject-level directory of processed data, which should have a
                        'summary' folder within (e.g./remote_home/bucklesh/Projects/TestData/ABCDPILOT_MSC02/)''')

    parser.add_argument('-v', '--verbose', dest="verbose", action="store_true", help="Tell me all about it.")

    parser.add_argument('--version', dest="verbose", action="version", version="%(prog)s_v" + VERSION,
                        help="Tell me all about it.")

    args = parser.parse_args()

    if args.subject_path:

        for sub in args.subject_path:

            sub_root = path.join(sub)

            if path.exists(sub_root):

                summary_path, data_path = image_summary.get_paths(sub_root)

            else:

                print 'no subject directory found within %s \nexiting...' % sub
                _logger.error('no subject directory within %s \nexiting...' % sub)

                return

            if path.exists(summary_path):

                img_out_path = path.join(sub_root, 'summary', 'img')
                img_in_path = summary_path
            else:
                print '\nMake sure a "summary" folder exists or this will not work...\n\tcheck in here: %s' % sub_root
                _logger.error('no Summary folder exists within %s' % sub_root)
                continue

            if not path.exists(img_out_path):

                try:

                    os.makedirs(img_out_path)

                except OSError:

                    print '\nCheck permissions to write to that path? \npath: %s' % summary_path
                    _logger.error('cannot make /img within /summary... permissions?')

                    return

            try:
                gifs = [gif for gif in os.listdir(img_in_path) if gif.endswith('gif')]

                if len(gifs) == 0:

                    _logger.error('no .gifs in summary folder')
                    print '\nNo summary .gifs were found! There should be some .gifs and I do not make those! '\
                        'Check to make sure the proper scripts have been ran? '

                    return

                else:

                    copy_images(img_in_path, gifs, img_out_path)

                    data = image_summary.get_list_of_data(data_path)

                    _logger.debug('data are: %s' % data)

            except OSError:

                    print 'Unable to locate image sources...'

                    return

            real_data = []
            epi_in_t1_gifs = sorted([path.join('./img', path.basename(gif)) for gif in gifs if '_in_t1.gif' in gif and 'atlas' not in gif])

            t1_in_epi_gifs = sorted([path.join('./img', path.basename(gif)) for gif in gifs if '_t1_in_REST' in gif])


            # now hack that subject_code on outa there
            split_gif = t1_in_epi_gifs[0].split('_')

            if len(split_gif) == 4:
                code = path.basename(split_gif[0])
                print 'CODE IS %s: ' % code
            elif len(split_gif) == 5:
                code = path.basename('_'.join(split_gif[0:2]))
            else:
                code = ''

            # Tell the people of this code from atop the mountain
            global subject_code
            subject_code = code

            print 'CODE IS %s: ' % code

            subject_code_folder = path.join(summary_path, code)

            if not path.exists(subject_code_folder):
                os.makedirs(subject_code_folder)

            # Check list of epi-data to ensure even numbers of files...
            # TODO: improve this section with a more specific test
            if len(data['epi-data']) % 2 != 0:  # we should have at least 1 raw REST and 1 SBRef per subject (pairs)

                _logger.warning('odd number of epi files were found...')
                alt_sbref_path = path.join(sub_root, 'MNINonLinear', 'Results')
                pattern = alt_sbref_path + '/REST?/REST?_SBRef.nii.gz'
                more_epi = glob.glob(pattern)

                for sbref in more_epi:
                    data['epi-data'].append(sbref)

            # SLICING UP EPI DATA

            for list_entry in data['epi-data']:

                # get modality so we can know how to slice it...
                modality = image_summary.get_subject_info(list_entry)[1]
                print 'PROCESSING subject_code: %s, modality: %s ' % (code, modality)
                print 'slicing up %s' % list_entry

                if 'REST' in modality and 'SBRef' not in modality:

                    image_summary.slice_list_of_data([list_entry], subject_code=subject_code, modality=modality,
                                                     dest_dir=img_out_path, also_xyz=True)

                elif 'SBRef' in modality and 'REST' in modality:
                    modality, series = image_summary.get_subject_info(list_entry)[1], image_summary.get_subject_info(list_entry)[2]
                    image_summary.slice_image_to_ortho_row(list_entry, path.join(img_out_path, '%s.png' % (modality)))

            # ITERATE through data dictionary keys, sort the list (value), then iterate through each list for params
            for list_entry in data.values():

                list_entry = sorted(list_entry)

                for item in list_entry:

                    print '\nadding %s to list of data, for which we need parameters...\n' % item
                    _logger.debug('data_list is: %s' % data)
                    params_row = image_summary.get_nii_info(item)
                    real_data.append(params_row)

            ##################
            #  START TO BUILD THE LAYOUT

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

            # INITIALIZE AND BUILD NEW LIST WITH MATCHED SERIES CODES FOR EACH EPI-TYPE
            print 'Assembling epi-images to build panel...'
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
                    _logger.debug('epi_rows were: %s' % epi_rows)
                    epi_rows = []

            # COMPLETE EPI PANEls

            newer_body += epi_panel_footer

            _logger.debug('newer_body is : %s' % newer_body)

            # TODO: fix this
            shutil.copy(path.join(img_in_path, 'DVARS_and_FD_CONCA.png'), img_out_path)
            dvars_path = path.join(img_out_path, 'DVARS_and_FD_CONCA.png')

            try:
                copy_images(img_in_path, structural_img_labels, img_out_path)  # /summary/img/<blah>

            except IOError:
                _logger.warning('unable to locate some images. Do they even exist?')
                print 'Make sure you have the structural .png available for this subject: %s' % subject_code
                print 'Expected path to Structural images: %s' % img_in_path
                print 'DVARS expected here: %s' % img_in_path

            # FILL-IN THE CODE / VERSION INFO
            new_html_header = edit_html_chunk(head, 'CODE', subject_code)
            new_html_header = edit_html_chunk(new_html_header, 'VERSION', 'Executive Summary_v' + VERSION)

            # ASSEMBLE THE WHOLE DOC, THEN WRITE IT!

            html_doc = new_html_header + newer_body + write_dvars_panel(path.join('./img', path.basename(dvars_path))) + html_footer

            write_html(html_doc, summary_path, title='executive_summary_%s.html' % subject_code)

            summary_root = path.join('/group_shares/PSYCH/code/release/utilities/executive_summary')

            move_cmd = "mv %(data_path)s/*.html %(sub_code_folder)s; mv %(data_path)s/img %(sub_code_folder)s" % {
                        'sub_code_folder': subject_code_folder,
                        'data_path'      : img_in_path}

            print '\n %s' % move_cmd

            _logger.debug(move_cmd)

            image_summary.submit_command(move_cmd)
            #copy_script_location = path.join(summary_root, 'helpers/copy_summary_data.sh')

            #shutil.copy(copy_script_location, summary_path)

    else:
        print 'no subject path provided!'
        _logger.error('no subject path provided!')

if __name__ == '__main__':

    main()

    print '\nall done!'
