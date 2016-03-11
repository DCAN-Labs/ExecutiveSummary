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

PROG = 'Layout Builder'
VERSION = '0.3.0'

LAST_MOD = '3-10-16'

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
    finally:
        f.close()

html_header = """<!DOCTYPE html>
<html lang = "en">
    <head>
        <meta charset = "utf-8">
        <title>Executive Summary: summary_tools</title>
        <style type="text/css">.epi,.grayords,.params{position:relative}.header,button,table,td{text-align:center}body{background-color:#c3c4c3}span{font-size:10px}img{border-radius:5px}.header{font-family:Garamond;margin-top:25px;margin-bottom:15px}table,td{border:1px dashed #70b8ff}.epi td,.params td,.top-left-panel table,td{border:none}.top-left-panel{float:left;width:50%}.top-left-panel img{width:250px;height:200px}.epi{float:right}.epi img{width:175px;height:150px}.params{float:left;width:40%}.params th{border-bottom:1px #70b8ff solid}.params .column-names{border-bottom:1px #00f solid;font-weight:700}.grayords{float:right}.grayords img{width:250px;height:200px}.out-of-range{color:red}button{cursor:pointer;display:inline-block;height:20px;width:70px;font-family:arial;font-weight:700;margin-top:2px}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>CODE</h1>
            <p>vVERSION</p>
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
                <table class="epi">
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
        <script>$(document).ready(function(){$("img[src*=SBRef]").width(300).height(110),$(".t1_tr").each(function(t,a){"2400.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t1_te").each(function(t,a){"4.97"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t1_x").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t1_y").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t1_z").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_frames").each(function(t,a){"120"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_x").each(function(t,a){"3.8"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_y").each(function(t,a){"3.8"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_z").each(function(t,a){"3.8"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_tr").each(function(t,a){"2100.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_te").each(function(t,a){"5.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_x").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_y").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_z").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_tr").each(function(t,a){"3200.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_te").each(function(t,a){"4.97"!=$(a).text()&&$(a).addClass("out-of-range")}),$("div.params").draggable(),$("div.grayords").draggable(),$("div.epi").draggable()});
        </script>
    </body>
</html>
"""


def convert_image_paths(list_of_images, src_location):

    new_image_paths = []
    for image in list_of_images:
        img_path = path.join(os.path.abspath(path.join(src_location, image)))
        if path.exists(img_path):
            new_image_paths.append(img_path)
        else:
            continue

    return new_image_paths


def get_image_path(image_string):
    return path.join(image_string)


def write_structural_panel(list_of_image_paths):

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
                        <td><a href="%(T1-left)s" target="_blank"><img src="./%(T1-left)s"></a></td>
                        <td><a href="%(T1-middle)s" target="_blank"><img src="./%(T1-middle)s"></a></td>
                        <td><a href="%(T1-right)s" target="_blank"><img src="./%(T1-right)s"></a></td>
                    </tr>
                    <tr>
                        <td><a href="%(T2-left)s" target="_blank"><img src="./%(T2-left)s"></a></td>
                        <td><a href="%(T2-middle)s" target="_blank"><img src="./%(T2-middle)s"></a></td>
                        <td><a href="%(T2-right)s" target="_blank"><img src="./%(T2-right)s"></a></td>
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

    if len(list_of_data) != 8:
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
                        <td><a href="%(rest_in_t1)s"><img src="%(rest_in_t1)s"></a></td>
                        <td><a href="%(t1_in_rest)s"><img src="%(t1_in_rest)s"></a></td>
                        <td><a href="%(sb_ref)s"><img src="%(sb_ref)s"></a></td>
                        <td><a href="%(rest_nonlin_norm)s"><img src="%(rest_nonlin_norm)s"></a></td>
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


def write_dvars_panel(dvars_input_path='./DVARS_and_FD_CONCA.png'):

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


def make_img_list(path_to_dir):

    images = []
    for image in os.listdir(path_to_dir):
        if image.endswith('.png') or image.endswith('gif'):
            images.append(get_image_path(image))

    return images


def append_html_with_chunk(existing_html, string_to_insert):

    new_html_string = existing_html + string_to_insert

    return new_html_string


def main():

    parser = argparse.ArgumentParser(description=program_desc, prog=PROG)

    parser.add_argument('-i', '--image-path', action="store", dest='img_dir', help="Provide a full path to the folder "
                                                                                   "containing summary images.")

    parser.add_argument('-s', '--subject_path', dest='subject_path', action='append', nargs='+', help='''
        Path to given subject folder under a given project e.g.
       /remote_home/bucklesh/Projects/TestData/ABCDPILOT_MSC02/''')

    parser.add_argument('-v', '--verbose', dest="verbose", action="store_true", help="Tell me all about it.")

    parser.add_argument('--version', dest="verbose", action="version", version="%(prog)s_v" + VERSION)

    args = parser.parse_args()

    # TODO: still need these?
    if args.img_dir:

        images_dir = path.join(args.img_dir)

        if path.exists(images_dir):

            image_set = make_img_list(images_dir)

            image_paths = convert_image_paths(image_set, images_dir)

            if len(image_paths) == 0:
                print 'no images found! exiting...'
                return
            else:
                print 'images found: %s' % image_paths
                return

    if args.subject_path:
        for sub in args.subject_path:
            sub_root = path.join(sub)[0]

            try:
                summary_path, data_path = image_summary.get_paths(sub_root)
                if path.exists(summary_path):
                    img_out_path = path.join(sub_root, 'summary', 'img')
                    img_in_path = summary_path
                    os.chdir(summary_path)  # fail if not?
                    if not path.exists(img_out_path):
                        try:
                            os.makedirs(img_out_path)
                        except OSError:
                            print '\nCheck permissions to write to that path? \npath: %s' % summary_path
                            _logger.error('cannot make /img within /summary... permissions?')
                            return
            except TypeError:

                print 'no summary data within %s \nexiting...' % args.subject_path

            try:
                gifs = [gif for gif in os.listdir(img_in_path) if gif.endswith('gif')]

                if len(gifs) == 0:
                    _logger.error('no gifs in summary folder')
                    print '\nNo .gifs were found! There should be some .gifs and I do not make those! '\
                        'Check to make sure the proper scripts have been ran? '

                    return
                else:
                    data = image_summary.get_list_of_data(data_path)

                    #print 'data are: %s' % data

            except:

                    print 'Images_in_Path does not exist because the summary folder is not there...'
                    return

            real_data = []

            # MAKE SOME REAL DATA PATHS

            if len(data['epi-data']) % 2 != 0:  # we should have at least 1 raw REST and 1 SBRef per subject (pairs)
                _logger.error('odd number of epi files were found...')
                alt_sbref_path = path.join(sub_root, 'MNINonLinear', 'Results')
                pattern = alt_sbref_path + '/REST?/REST?_SBRef.nii.gz'
                more_epi = glob.glob(pattern)
                for sbref in more_epi:
                    data['epi-data'].append(sbref)

            for list_entry in data['epi-data']:
                print 'slicing up %s' % list_entry
                code, modality, series = image_summary.get_subject_info(list_entry)
                if 'REST' in modality:
                    image_summary.slice_image_to_ortho_row(list_entry, path.join(img_out_path, '%s.png' % modality))
                elif 'SBRef' in modality:
                    image_summary.slice_image_to_ortho_row(list_entry, path.join(img_out_path, '%s_%s.png' % (series, modality)))

                print 'PROCESSING subject_code: %s, modality: %s ' % (code, modality)

            for list_entry in data.values():

                list_entry = sorted(list_entry)

                for item in list_entry:

                    print '\nadding %s to list of data, for which we need parameters...\n' % item
                    _logger.debug('data_list is: %s' % data)
                    params_row = image_summary.get_nii_info(item)
                    real_data.append(params_row)

            # START TO BUILD THE LAYOUT

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

            pngs = [png for png in os.listdir(img_out_path) if png.endswith('png')]

            # BUILD THE LISTS NEEDED FOR EPI-PANEL

            epi_in_t1_gifs = sorted([path.basename(path.join(summary_path,
                                                         gif)) for gif in gifs if '_in_t1.gif' in gif and 'atlas' not in gif])

            t1_in_epi_gifs = sorted([path.basename(path.join(summary_path, gif)) for gif in gifs if '_t1_in_REST' in gif])

            rest_raw_paths = sorted([path.join('./img', img) for img in pngs if 'SBRef' not in img])

            sb_ref_paths = sorted([path.join('./img', img) for img in pngs if 'SBRef' in img])

            # INITIALIZE AND BUILD NEW LIST WITH MATCHED SERIES CODES FOR EACH EPI-TYPE
            print 'Assembling epi-images to build panel...'
            epi_rows = []

            num_epi_gifs = len(t1_in_epi_gifs)

            if num_epi_gifs != len(epi_in_t1_gifs):
                _logger.error('incorrect number of gifs !\nepi_in_t1 count: %s\nt1_in_epi_count: %s' %(len(epi_in_t1_gifs), num_epi_gifs))
                print 'ack, something went wrong while trying to assemble epi-data! exiting...'
                return
            elif num_epi_gifs != len(rest_raw_paths):
                _logger.error('incorrect number of raw epi files!\nepi_rows: %s\nnum_epi_files: %s' %(len(rest_raw_paths), num_epi_gifs))
                print 'ack, something went wrong while trying to assemble epi-data! exiting...'
                return
            elif num_epi_gifs != len(sb_ref_paths):
                _logger.error('incorrect number of sb_ref files!\nepi_rows: %s\nnum_epi_files: %s' %(len(sb_ref_paths), num_epi_gifs))
                print 'ack, something went wrong while trying to assemble epi-data! exiting...'
                return
            else:
                newer_body = new_body + epi_panel_header
                for i in range(0, num_epi_gifs):
                    epi_rows.append(epi_in_t1_gifs.pop(0))
                    epi_rows.append(t1_in_epi_gifs.pop(0))
                    epi_rows.append(rest_raw_paths.pop(0))
                    epi_rows.append(sb_ref_paths.pop(0))
                    newer_body += write_epi_panel_row(epi_rows[:4])
                    _logger.debug('epi_rows were: %s' % epi_rows)
                    epi_rows = []

                #print newer_body

            head = html_header

            # TODO: adjust this more so that we can build more dynamically and not hard-coded numbers of rows
            # APPEND OLD BODY WITH NEW EPI-PANEL SECTIONS

            newer_body += epi_panel_footer

            _logger.debug('newer_body is : %s' % newer_body)

            # FILL-IN THE CODE / VERSION INFO
            new_html_header = edit_html_chunk(head, 'CODE', code)
            new_html_header = edit_html_chunk(new_html_header, 'VERSION', image_summary.VERSION)

            # ASSEMBLE THE WHOLE DOC, THEN WRITE IT!
            dvars_path = path.join('./DVARS_and_FD_CONCA.png')

            html_doc = new_html_header + newer_body + write_dvars_panel(dvars_path) + html_footer

            write_html(html_doc, summary_path, title='executive_summary_%s.html' % code)

        else:
            print 'no subject path provided!'
            _logger.error('no subject path provided!')
            return

if __name__ == '__main__':

    main()

    print '\nall done!'
