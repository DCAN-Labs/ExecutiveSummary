#!/usr/bin/env python
"""
__author__ = 'Shannon Buckley', 2/20/16

Call this program with -s, pointing to a subject-summary_tools path, to build the Executive Summary for that subject's processed
data.
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
        <title>Executive Summary: summary_tools</title>
        <style type="text/css">.epi,.grayords,.params{position:relative}.header,button,table,td{text-align:center}body{background-color:#c3c4c3}span{font-size:10px}img{border-radius:5px}.header{font-family:Garamond;margin-top:25px;margin-bottom:15px}table,td{border:1px dashed #70b8ff}.epi td,.params td,.top-left-panel table,td{border:none}.top-left-panel{float:left;width:50%}.top-left-panel img{width:250px;height:200px}.epi{float:right}.epi img{width:175px;height:150px}.params{float:left;width:40%}.params th{border-bottom:1px #70b8ff solid}.params .column-names{border-bottom:1px #00f solid;font-weight:700}.grayords{float:right}.grayords img{width:250px;height:200px}.out-of-range{color:red}button{cursor:pointer;display:inline-block;height:20px;width:70px;font-family:arial;font-weight:700;margin-top:2px}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>summary_tools</h1>
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
        <script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.9.1/jquery-ui.min.js"></script>
        <script>$(document).ready(function(){function e(){console.log("x: "+this.x.text()),console.log("y: "+this.y),console.log("z: "+this.z),1!=parseFloat(this.x.text())&&(console.log(this.x+" is out of range!"),this.x.addClass("out-of-range"))}var t=Array($(".t1_x"),$(".t1_y"),$(".t1_z"));console.log(t.length),console.log(t[0].childNodes);var a=$("#t1_tr").text();2400!=Number(a)&&(console.log(a+" is not equal to 2400"),$("#t1_tr").addClass("out-of-range"));var o={x:$(".t1_x"),y:$(".t1_y"),z:$(".t1_z")};o.logDetails=e,o.logDetails(),"1.0"!=$(".t1_x").text()&&$(".t1_x").addClass("out-of-range"),"1.0"!=$(".t1_y").text()&&$(".t1_y").addClass("out-of-range"),"1.0"!=$(".t1_z").text()&&$(".t1_z").addClass("out-of-range"),"1.0"!=$(".t2_x").text()&&$(".t2_x").addClass("out-of-range"),"1.0"!=$(".t2_y").text()&&$(".t2_y").addClass("out-of-range"),"1.0"!=$(".t2_z").text()&&$(".t2_z").addClass("out-of-range"),"5.0"!=$("#epi1_te").text()&&$("#epi1_te").addClass("out-of-range"),"5.0"!=$("#epi2_te").text()&&$("#epi2_te").addClass("out-of-range"),"5.0"!=$("#epi3_te").text()&&$("#epi3_te").addClass("out-of-range"),"5.0"!=$("#epi4_te").text()&&$("#epi4_te").addClass("out-of-range"),"5.0"!=$("#epi5_te").text()&&$("#epi5_te").addClass("out-of-range"),"120"!=$("#epi1_frames").text()&&$("#epi1_frames").addClass("out-of-range"),"120"!=$("#epi2_frames").text()&&$("#epi2_frames").addClass("out-of-range"),"120"!=$("#epi3_frames").text()&&$("#epi3_frames").addClass("out-of-range"),"120"!=$("#epi4_frames").text()&&$("#epi4_frames").addClass("out-of-range"),"120"!=$("#epi5_frames").text()&&$("#epi5_frames").addClass("out-of-range"),"3.8"!=$("#epi1_x").text()&&$("#epi1_x").addClass("out-of-range"),"3.8"!=$("#epi1_y").text()&&$("#epi1_y").addClass("out-of-range"),"3.8"!=$("#epi1_z").text()&&$("#epi1_z").addClass("out-of-range"),"3.8"!=$("#epi2_x").text()&&$("#epi2_x").addClass("out-of-range"),"3.8"!=$("#epi2_y").text()&&$("#epi2_y").addClass("out-of-range"),"3.8"!=$("#epi2_z").text()&&$("#epi2_z").addClass("out-of-range"),"3.8"!=$("#epi3_x").text()&&$("#epi3_x").addClass("out-of-range"),"3.8"!=$("#epi3_y").text()&&$("#epi3_y").addClass("out-of-range"),"3.8"!=$("#epi3_z").text()&&$("#epi3_z").addClass("out-of-range"),"3.8"!=$("#epi4_x").text()&&$("#epi4_x").addClass("out-of-range"),"3.8"!=$("#epi4_y").text()&&$("#epi4_y").addClass("out-of-range"),"3.8"!=$("#epi4_z").text()&&$("#epi4_z").addClass("out-of-range"),"3.8"!=$("#epi5_x").text()&&$("#epi5_x").addClass("out-of-range"),"3.8"!=$("#epi5_y").text()&&$("#epi5_y").addClass("out-of-range"),"3.8"!=$("#epi5_z").text()&&$("#epi5_z").addClass("out-of-range"),$("div.params").draggable(),$("div.grayords").resizable(),$("div.grayords").draggable(),$("div.epi").draggable()});
        </script>
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

    parser.add_argument('-s', '--subject_path', dest='subject_path', nargs='*', help='''
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

        try:
            summary_path, data_path = image_summary.get_paths(sub_root)
            if summary_path:
                img_out_path = path.join(sub_root, 'summary', 'img')
                img_in_path = summary_path
                gifs = [gif for gif in os.listdir(img_in_path) if gif.endswith('gif')]

                if not path.exists(img_out_path):
                    os.makedirs(img_out_path)

        except TypeError:

                print 'no summary data! exiting...'
                return

        except UnboundLocalError:
            print 'oops, wrong type'

    structural_img_labels = ['T1-Sagittal-Insula-FrontoTemporal.png',
                             'T1-Axial-BasalGangila-Putamen.png',
                             'T1-Coronal-Caudate-Amygdala.png',
                             'T2-Sagittal-Insula-FrontoTemporal.png',
                             'T2-Axial-BasalGangila-Putamen.png',
                             'T2-Coronal-Caudate-Amygdala.png'
                             ]

    real_data = []

    # MAKE SOME REAL DATA PATHS
    summary_path, data_path = image_summary.get_paths(sub_root)

    os.chdir(summary_path) # fail if not?

    data = image_summary.get_list_of_data(sub_root)

    print 'data are: %s' % data

    for list_entry in data['epi-data']:
        print 'slicing up %s' % list_entry
        code, modality, series = image_summary.get_subject_info(list_entry)
        image_summary.slice_image_to_ortho_row(list_entry, path.join(img_out_path, '%s.png' % modality))

    print 'PROCESSING summary_tools: %s' % code

    for list_entry in data.values():

        list_entry = sorted(list_entry)

        for item in list_entry:

            print '\nadding %s to list of data, for which we need parameters...\n' % item
            # _logger.debug('data_list is: %s' % data)
            params_row = image_summary.get_nii_info(item)
            real_data.append(params_row)

    # START TO BUILD THE LAYOUT

    html_params_panel = param_table_html_header

    # BUILD PARAM PANEL

    for data_row in real_data:
        html_params_panel += write_param_table_row(data_row)

    html_params_panel += param_table_footer

    # BUILD & WRITE THE STRUCTURAL PANEL

    body = write_structural_panel(structural_img_labels)

    # APPEND WITH PARAMS PANEL

    new_body = body + html_params_panel

    pngs = [png for png in os.listdir(img_out_path) if png.endswith('png')]

    # BUILD THE LISTS NEEDED FOR EPI-PANEL

    epi_in_t1_gifs = sorted([path.basename(path.join(summary_path,
                                                 gif)) for gif in gifs if '_in_t1.gif' in gif and 'atlas' not in gif])

    t1_in_epi_gifs = sorted([path.basename(path.join(summary_path, gif)) for gif in gifs if '_t1_in_REST' in gif])

    sb_ref_paths = [path.join('./img', 'SBRef' + img + '.png') for img in pngs]

    rest_raw_paths = sorted([path.join('./img', img) for img in pngs if 'SBRef' not in img])

    # INITIALIZE AND BUILD NEW LIST WITH MATCHED SERIES CODES FOR EACH EPI-TYPE

    epi_rows = []

    num_epi_files = len(epi_in_t1_gifs)

    for i in range(0, num_epi_files-1):
        epi_rows.append(epi_in_t1_gifs[i])
        epi_rows.append(t1_in_epi_gifs[i])
        epi_rows.append(sb_ref_paths[i])
        epi_rows.append(rest_raw_paths[i])

    head = html_header

    # TODO: adjust this more.
    # APPEND OLD BODY WITH NEW EPI-PANEL SECTIONS
    newer_body = new_body + epi_panel_header + write_epi_panel_row(epi_rows[:4]) + write_epi_panel_row(epi_rows[4:8]) \
                 + write_epi_panel_row(epi_rows[8:12]) + write_epi_panel_row(epi_rows[12:16]) \
                 + write_epi_panel_row(epi_rows[16:20]) + epi_panel_footer

    # print 'newer_body is : %s' % newer_body

    # FILL-IN THE CODE / VERSION INFO
    new_html_header = edit_html_chunk(head, 'summary_tools', code)
    new_html_header = edit_html_chunk(new_html_header, 'VERSION', image_summary.VERSION)

    # ASSEMBLE THE WHOLE DOC, THEN WRITE IT!
    html_doc = new_html_header + newer_body + write_dvars_panel() + html_footer

    write_html(html_doc, summary_path)

if __name__ == '__main__':

    main()

    print '\nall done!'
