#!/usr/bin/env python
"""
__author__ = 'Shannon Buckley', 2/20/16
"""

import os
from os import path
import argparse
import image_summary

VERSION = '0.0.0'

LAST_MOD = '2-20-16'


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
        <title>Executive Summary</title>
        <link href="style.css" type="text/css" rel="stylesheet">

    </head>
    <body>
        <div class="header">
            <h1>%(subj_code)s</h1>
            <p>pipeline_v%(version)s</p>
            <div class="button" id="next-button">
                <button>Next</button>
            </div>
        </div>""" % {'subj_code': 'code',
                     'version'  : VERSION}


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

param_table_html_row_example = """
                        <tr class="t1_data">
                            <td>%(modality)s</td>
                            <td class="t1_x">%(x_dim)s</td>
                            <td class="t1_y">%(y_dim)s</td>
                            <td class="t1_z">%(z_dim)s</td>
                            <td id="t1_te" class="te">%(te)s</td>
                            <td id="t1_tr">%(tr)s</td>
                            <td>%(frames)s</td>
                            <td id="t1_ti">%(ti)s</td>
                        </tr>""" % {'modality'  : 'data_modality',
                                    'x_dim'     : 'pixdimx',
                                    'y_dim'     : 'pixdimy',
                                    'z_dim'     : 'pixdimz',
                                    'te'        : 'echo_time',
                                    'tr'        : 'repetition_time',
                                    'frames'    : 'n_frames',
                                    'ti'        : 'inversion_time'}

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
        <script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.9.1/jquery-ui.min.js"></script>
        <script src="script.js"></script>
    </body>
</html>
"""


def convert_image_paths(list_of_images, src_location, ext='.png'):

    new_image_paths = []
    for image in list_of_images:
        img_path = path.join(src_location, image + ext)
        if path.exists(img_path):
            new_image_paths.append(img_path)
        else:
            continue

    return new_image_paths


def get_image_path(image_string):
    return path.join(image_string)


def write_structural_panel(list_of_image_paths):

    if len(list_of_image_paths) < 6:
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
                            <td id="%(class_prefix)s_frames">%(frames)s</td>
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


def write_dvars_panel(dvars_path='./DVARS_and_FD_CONCA.png'):

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
            </div>""" % {'dvars_path' : dvars_path}

    return dvars_panel_html_string


def make_img_list(path_to_dir):

    images = []
    for image in path_to_dir:
        if image.endswith('.png'):
            image.append(get_image_path(image))

    return images


def append_html_with_chunk(existing_html, string_to_insert):

    new_html_string = existing_html + string_to_insert

    return new_html_string


def main():

    parser = argparse.ArgumentParser(description='html_layout_tester')

    parser.add_argument('-i', '--image-dir', action="store", dest='img_dir', help="Provide a full path to the "
                                                                                     "folder "
                                                                                     "containing all summary images.")

    parser.add_argument('-l', '--list_of_images', action="store", nargs='*', dest='images_list')

    parser.add_argument('-s', '--subject_path', dest='subject_path', help='''
        Path to given subject folder under a given project e.g.
       /remote_home/bucklesh/Projects/TestData/ABCDPILOT_MSC02/''')

    parser.add_argument('-v', '--verbose', dest="verbose", action="store_true", help="Tell me all about it.")

    args = parser.parse_args()

    if args.img_dir:

        images_dir = path.join(args.img_dir)

        if path.exists(images_dir):

            image_set = make_img_list(images_dir)

            image_paths = convert_image_paths(image_set, './img')

            print image_paths

    if args.images_list:
        print args.images_list
        for image in args.images_list:
            image_path = path.join('summary', '%s' % image)

            if path.exists(image_path):

                print 'image path is %s' % image_path

    if args.subject_path:
        sub_root = path.join(args.subject_path)
        img_in_path = path.join(sub_root, 'summary')
        img_out_path = path.join(img_in_path, 'img')
        data_in_path = image_summary.get_paths(sub_root)[1]

        pngs = [png for png in os.listdir(img_in_path) if png.endswith('png')]
        gifs = [gif for gif in os.listdir(img_in_path) if gif.endswith('gif')]

###############################
    # TEST WITH FAKE DATA
###############################

    structural_img_labels = ['T1-Sagittal-Insula-FrontoTemporal.png',
                             'T1-Axial-BasalGangila-Putamen.png',
                             'T1-Coronal-Caudate-Amygdala.png',
                             'T2-Sagittal-Insula-FrontoTemporal.png',
                             'T2-Axial-BasalGangila-Putamen.png',
                             'T2-Coronal-Caudate-Amygdala.png'
                             ]

    real_data = []

    # MAKE SOME REAL DATA FOR TESTING
    summary_path, data_path = image_summary.get_paths(sub_root)

    # see if changing to the local dir helps other issues
    os.chdir(summary_path)

    # THIS PART TAKES A WHILE... CONSIDER Chopping the function up a little?
    data = image_summary.get_list_of_data(sub_root)
    print 'data are: %s' % data
    img_out_path = path.join(summary_path, 'img')
    if not path.exists(img_out_path):
        os.makedirs(img_out_path)

    # TODO: figure out a better way to extract code
    code = 'ABCDPILOT_MSC02'

    #code = image_summary.get_subject_info(sub_root)[0]

    print 'PROCESSING code: %s' % code

    # TODO: this section is redundant given what 'get_list_of_data' achieves all at once
    # TODO: consider chopping up that method into smaller chunks of code or remove iterating twice
    for list_entry in data['epi-data']:
        print 'slicing up %s' % list_entry
        code, modality, series = image_summary.get_subject_info(list_entry)
        image_summary.slice_image_to_ortho_row(list_entry, path.join(img_out_path, '%s.png' % modality))

    for list_entry in data.values():

        for item in list_entry:

            print '\nadding %s to list of data, for which we need parameters...\n' % item
            #_logger.debug('data_list is: %s' % data)
            params_row = image_summary.get_nii_info(item)
            real_data.append(params_row)

    html_params_panel = param_table_html_header

    for data_row in real_data:
        html_params_panel += write_param_table_row(data_row)

    html_params_panel += param_table_footer

    body = write_structural_panel(structural_img_labels)

    new_body = body + html_params_panel

    # TODO: below is a mess... fix all this epi-panel-makin stuff
    # TODO: we may have fewer than 6, so do this better...
    gif_labels = ['REST1', 'REST2', 'REST3', 'REST4', 'REST5', 'REST6']

    epi_in_t1_gifs = sorted([path.basename(path.join(summary_path,
                                                 gif)) for gif in gifs if '_in_t1.gif' in gif and 'atlas' not in gif])

    t1_in_epi_gifs = sorted([path.basename(path.join(summary_path, gif)) for gif in gifs if '_t1_in_REST' in gif])

    sb_ref_paths = [path.join('./img', 'SBRef' + img + '.png') for img in gif_labels]

    # TODO: still need to slice these up then locate in the img_out location?
    non_lin_paths = [path.join(summary_path, img + '_nonlin_norm.png') for img in gif_labels]

    epi_rows = []

    for i in range(0, len(gif_labels)-1):
        epi_rows.append(epi_in_t1_gifs[i])
        epi_rows.append(t1_in_epi_gifs[i])
        epi_rows.append(sb_ref_paths[i])
        epi_rows.append(non_lin_paths[i])

    head = html_header

    newer_body = new_body + epi_panel_header + write_epi_panel_row(epi_rows[:4]) + write_epi_panel_row(epi_rows[4:8]) \
                 + write_epi_panel_row(epi_rows[8:12]) + write_epi_panel_row(epi_rows[12:16]) \
                 + write_epi_panel_row(epi_rows[16:20]) + epi_panel_footer

    # _logger.debug('newer_body is : %s' % newer_body)

    new_html_header = edit_html_chunk(head, 'code', code)

    # Test 1: Build the doc and write it as-is
    html_doc = new_html_header + newer_body + write_dvars_panel() + html_footer

    write_html(html_doc, summary_path)

    # Test 2: change the body and write the chunk
    # new_body = html_body.replace('t1-top-left', args.images_list[0])
    # new_body = html_body.replace('t1-middle', args.images_list[1])
    # new_body = html_body.replace('t1-top-right', args.images_list[2])

    # write_html(new_body, 'body-test-with-args')

if __name__ == '__main__':

    main()
