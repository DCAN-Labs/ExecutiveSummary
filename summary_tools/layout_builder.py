#! /usr/bin/env python

__doc__ = """
Builds the layout for the Executive Summary of the bids-formatted output from
the DCAN-Labs fMRI pipelines.
"""

__version__ = "2.0.0"

import os
from os import path
import re
import image_summary
import glob
import shutil
from constants import *


def make_tx_section(tx, img_in_path, img_out_path):
    """
    Make the brainsprite viewer for tx and a
    button and slider for viewing tx pngs.

    :parameter: tx: string to use in labels, names, patterns... (T1 v T2).
    :parameter: img_in_path: path to images (and to subdirectory) of images.
    :parameter: img_out_path: destination of images.
    :return: string of html containing the entire section for tx.
    """
    tx_section = ''
    tx_scripts = ''

    # Get the path to the pngs that will be used for the mosaic.
    tx_path = os.path.join(img_in_path, tx + '_pngs')

    if not os.path.isdir(tx_path):
        # Not all subjects have T1, T2.
        return tx_section, tx_scripts

    # The other pngs we need are in the img_in_path. Get those pngs so users
    # can see the higher res images when they want to.
    image_list = sorted(find_and_copy_images(img_in_path, tx + '-*.png', img_out_path))

    # As the images are added to the html, they are given a class. When the
    # script for the slider is called, it will allow the user to browse all
    # of the images of the class provided. Therefore, each slider must have
    # its own class.
    image_class = tx + 'pngs'
    modal_id = tx + '-modal'
    modal_container = ''
    modal_container, slider_scripts = make_modal_slider(modal_id, image_class, image_list)
    tx_scripts += slider_scripts

    # Make a button to open the modal container.
    modal_button = ''
    slider_label = 'View %s pngs' % tx
    if modal_container is not '':
        modal_button = """ <button class="w3-btn w3-teal"
            onclick="document.getElementById('%(modal_id)s').style.display='block'">%(slider_label)s</button>
            """ % { 'modal_id'    : modal_id,
                    'slider_label': slider_label }

    # Make the brainsprite viewer.
    brainsprite_label, brainsprite_viewer, brainsprite_loader = make_brainsprite_viewer (tx, tx_path, img_out_path)
    tx_scripts += brainsprite_loader

    tx_section += TX_SECTION % {
            'tx'                : tx,
            'brainsprite_label' : brainsprite_label,
            'modal_button'      : modal_button,
            'brainsprite_viewer': brainsprite_viewer }

    # HTML for the modal container should be tacked on the end.
    tx_section += modal_container

    return tx_section, tx_scripts


def make_modal_slider(modal_id, image_class, image_list):
    """
    Make a modal container with a button to close the container in the
    upper right. The container will contain a slider/carousel to display
    the images in the list with the class supplied.

    :parameter: modal_id: id to identify the container.
    :parameter: image_class: contents of slider will be of this class.
    :parameter: image_list: list of images thru which to cycle.
    :return: string of html with beginning of modal container.
    """
    modal_container = ''
    slider_scripts = ''

    numimages = len(image_list)
    if numimages is 0:
        return modal_container, slider_scripts

    # Just a sanity check, since we happen to know how many to expect.
    if numimages is not 9:
        # TODO: WARNING only:
        print('Expected 9 pngs for %s but found %s.' % (tx, numimages))


    # Start a modal container with the id supplied.
    modal_container += """
        <div id="%(modal_id)s" class="w3-modal">
            <div class="w3-modal-content">
                <div class="w3-content w3-display-container">
        """ % { 'modal_id' : modal_id }

    # Add the images.
    for image_file in image_list:
        image_name=os.path.basename(image_file)
        modal_container += """
        <div class="w3-display-container %(image_class)s">
            <img src="%(image_file)s" style="width:%(width)s">
            <div class="w3-display-topleft w3-black"><p>%(image_name)s</p></div>
        </div>
        """ % {
            'image_class': image_class,
            'image_file' : image_file,
            'width'      : '100%',
            'image_name' : image_name
            }
    # Add the right/left buttons, the close button, and the end of the container.
    modal_container += MODAL_SLIDER_END % {
            'modal_id'   : modal_id,
            'image_class': image_class }

    slider_scripts += SLIDER_SCRIPTS % { 'image_class': image_class }

    return modal_container, slider_scripts


def make_brainsprite_viewer(tx, tx_path, images_path):
    """
    Builds HTML for BrainSprite viewer so users can click through 3d anatomical images.

    :parameter: tx: string to use in labels, names, patterns... (T1 v T2).
    :parameter: tx_path: path to the pngs to be used to make the mosaic.
    :parameter: images_path: absolute destination for mosaic image.

    :return: strings of html containing the rows with a canvas and 'hidden' BrainSprite mosaic image
    """
    spritelabel = ''
    spriteviewer = ''
    spriteloader = ''

    # Make sure there is data for this path.
    if os.path.isdir(tx_path):
        spritelabel += '<h6>BrainSprite Viewer: %s</h6>' % tx

        print('Making brainsprite mosaic from %s pngs.' % tx )
        mosaic_name = '%s_mosaic.jpg' % tx
        out_path = os.path.join(images_path, mosaic_name)
        image_summary.make_mosaic(tx_path, out_path)

        viewer = tx + '-viewer'
        spriteImg = tx + '-spriteImg'

        spriteviewer += SPRITE_VIEWER_HTML % {
                'tx'         : tx,
                'viewer'     : viewer,
                'spriteImg'  : spriteImg,
                'mosaic_path': rel_img_path(mosaic_name),
                'width'      : '100%' }

        spriteloader += SPRITE_LOAD_SCRIPT % {
                'tx'        : tx,
                'viewer'    : viewer,
                'spriteImg' : spriteImg }

    return spritelabel, spriteviewer, spriteloader


def make_combined_section(paths, placeholders, images_path):

    combined = """
        <section id="Combined">
    """

    # Find concatenated gray plots.
    values = IMAGE_INFO['concat_pre_reg_gray']
    source_path = paths[values['paths_key']]
    pre_reg_gray = find_and_copy_image(source_path, values['pattern'], images_path)
    if pre_reg_gray is None:
        pre_reg_gray = placeholders[values['placeholders_key']]

    values = IMAGE_INFO['concat_post_reg_gray']
    source_path = paths[values['paths_key']]
    post_reg_gray = find_and_copy_image(source_path, values['pattern'], images_path)
    if post_reg_gray is None:
        post_reg_gray =  placeholders[values['placeholders_key']]

    # Get T1 in atlas and atlas in T1.
    values = IMAGE_INFO['atlas_in_t1']
    source_path = paths[values['paths_key']]
    atlas_in_t1 = find_and_copy_image(source_path, values['pattern'], images_path)
    if atlas_in_t1 is None:
        atlas_in_t1 =  placeholders[values['placeholders_key']]

    values = IMAGE_INFO['t1_in_atlas']
    source_path = paths[values['paths_key']]
    t1_in_atlas = find_and_copy_image(source_path, values['pattern'], images_path)
    if t1_in_atlas is None:
        t1_in_atlas =  placeholders[values['placeholders_key']]

    atlas_row = """
        <div class="w3-container">
            <div class="w3-row">
                <div class="w3-col s6 w3-center"><h6>Resting State Grayordinates Plots</h6></div>
            <div class="w3-row">
            <div>
                <div class="w3-col s3 w3-center"><h6>Pre-Regression</h6></div>
                <div class="w3-col s3 w3-center"><h6>Post-Regression</h6></div>
                <div class="w3-col s3 w3-center"><h6>Atlas in T1</h6></div>
                <div class="w3-col s3 w3-center"><h6>T1 in Atlas</h6></div>
            </div>
            <br>
            <div  class="w3-row-padding">
                <div class="w3-col s3"><img src="%(pre_reg_gray)s" style="width:%(width)s"></div>
                <div class="w3-col s3"><img src="%(post_reg_gray)s" style="width:%(width)s"></div>
                <div class="w3-col s3"><img src="%(atlas_in_t1)s" style="width:%(width)s"></div>
                <div class="w3-col s3"><img src="%(t1_in_atlas)s" style="width:%(width)s"></div>
            </div>
            <br>
        </div>
    """ % {'pre_reg_gray'      : pre_reg_gray,
           'post_reg_gray'     : post_reg_gray,
           'atlas_in_t1'       : atlas_in_t1,
           't1_in_atlas'       : t1_in_atlas,
            'width'             : '100%'}

    combined += atlas_row + '</section>'
    return combined

def make_tasks_section(task_entries, paths, placeholders, images_path):

    tasks_section = ''

    if len(task_entries) is 0:
        print('No tasks were found for %s, %s.' % (self.subject_id, self.session_id))
        return tasks_section

    # Add column headings.
    tasks_section += TASKS_HEADER

    # Each entry in task_entries is a tuple of the task-name (without
    # task-) and run number (without run-).

    # Add a row for each task.
    for task_name, task_num in task_entries:
        row_label = 'task-%s run-%s' % (task_name, task_num)

        # Clear the list of the files needed for this task.
        task_files = []

        # Using glob patterns to find the files for this task; start
        # with a pattern for the task/run itself.
        task_pattern = task_name + '*' + task_num

        # For the processed files, it's as simple as looking for the pattern in
        # the source-directory.
        for key in [ 'task_pre_reg_gray', 'task_post_reg_gray', 'task_in_t1', 't1_in_task' ]:
            values = IMAGE_INFO[key]
            pattern = values['pattern'] % task_pattern
            source_path = paths[values['paths_key']]
            task_file = find_and_copy_image(source_path, pattern, images_path)
            if task_file:
                task_files.append(task_file)
            else:
                task_files.append(placeholders[values['placeholders_key']])

        # For the unprocessed files, it's more complicated.
        # Find a reference file for this task.
        values = IMAGE_INFO['sbref']
        pattern = values['pattern'] % task_pattern
        source_path = paths[values['paths_key']]
        ref_file = find_one_file(source_path, pattern)
        if ref_file is None and task_num is '01':
            # Run is not required by BIDS when there is only 1 run for a task.
            # Try again with task name only (no run).
            pattern = values['pattern'] % task_name
            ref_file = find_one_file(source_path, pattern)

        # If the reference file was found in bids input, just replace the
        # extension(s) with .png to make the name of the output file.
        if ref_file:
            png_file = nifti_root(ref_file) + '.png'
        else:
            # Next best thing: try to find a scout file.
            values = IMAGE_INFO['scout']
            pattern = values['pattern'] % task_pattern
            source_path = paths[values['paths_key']]
            ref_file = find_one_file(source_path, pattern)
            if ref_file:
                # Use the name of the file's parent directory to make a name
                # for the output file. Else we would have name collisions,
                # since these are all named 'scout'.
                parent_path = os.path.dirname(ref_file)
                parent = os.path.basename(parent_path)
                png_file = parent + '_sbref.png'

        # Now have path to input and name for output.
        # Slice the .nii to get the .png.
        if ref_file is not None:
            dest_file = os.path.join(images_path, png_file)
            image_summary.slice_image_to_ortho_row(ref_file, dest_file)
            # TODO: make sure this made a relative filename in the html!
            task_files.append(dest_file)
        else:
            task_files.append(placeholders[IMAGE_INFO['sbref']['placeholders_key']])

        # Find the bids input file for this task.
        values = IMAGE_INFO['bold']
        pattern = values['pattern'] % task_pattern
        source_path = paths[values['paths_key']]
        bold_file = find_one_file(source_path, pattern)
        if bold_file is None and task_num is '01':
            # Run is not required by BIDS when there is only 1 run for a task.
            pattern = values['pattern'] % task_name
            bold_file = find_one_file(source_path, pattern)

        # Slice the .nii to get the .png.
        if bold_file:
            png_file = nifti_root(bold_file) + '.png'
            dest_file = os.path.join(images_path, png_file)
            image_summary.slice_image_to_ortho_row(bold_file, dest_file)
            # TODO: make sure this made a relative filename in the html!
            task_files.append(dest_file)
        else:
            task_files.append(placeholders[values['placeholders_key']])

        # Finally, have all of the files for this task/run; get the html.
        tasks_section += write_task_row(task_files, row_label)

    # Add the end of the tasks section.
    tasks_section += TASKS_END

    return tasks_section


def write_task_row(list_of_img_paths, row_label):
    """
    Takes a list of image paths and builds one row of images.

    :parameter: list_of_img_paths: list of paths
    :parameter: row_label: name of the task
    :return: row of task's images
    """

    task_row = """
        <div class="w3-row-padding">
            <div class="w3-col s1 w3-left">%(row_label)s</div>
            <div class="w3-col s2"><img src="%(dvars_prereg)s" style="width:%(width)s"></div>
            <div class="w3-col s2"><img src="%(dvars_postreg)s" style="width:%(width)s"></div>
            <div class="w3-col s2"><img src="%(task_in_t1)s" style="width:%(width)s"></div>
            <div class="w3-col s2"><img src="%(t1_in_task)s" style="width:%(width)s"></div>
            <div class="w3-col s3"><img src="%(ref)s" style="width:%(width)s; padding: 2px"></div>
            <br>
            <div class="w3-col s3"><img src="%(bold)s" style="width:%(width)s; padding: 2px"></div>
        </div>
        """ % {'row_label'         : row_label,
               'dvars_prereg'      : list_of_img_paths[0],
               'dvars_postreg'     : list_of_img_paths[1],
               'task_in_t1'        : list_of_img_paths[2],
               't1_in_task'        : list_of_img_paths[3],
               'ref'               : list_of_img_paths[4],
               'bold'              : list_of_img_paths[5],
               'width'             : '100%'}

    return task_row




def rel_img_path(filepath):
    """
    Turns a file path into the relative path used by executive summary.
    That is, prepends ./img/ to the file's name.

    :parameter: filepath: path to file
    :return: relative path
    """

    return os.path.join('./img/', os.path.basename(filepath))

def nifti_root(filename):
    """
    Gets the root filename from a nifti file. That is, strips off both
    the dirname and extension(s).

    :parameter: filename.
    :return: filename with no dirname or extensions.
    """

    # File may be either .nii or .nii.gz.
    root, ext = os.path.splitext(os.path.basename(filename))
    if ext == '.gz':
        root, ext = os.path.splitext(root)

    return root


def find_and_copy_images(seek_dir, pattern, image_path):
    """
    Finds all files within the directory specified that match
    the glob-style pattern. Copies each file to the directory
    of images.

    :parameter: seek_dir: directory to be searched.
    :parameter: pattern: Unix shell pattern for finding files.
    :parameter: image_path: directory of images.
    :return: list of relative paths of copied files (may be empty).
    """
    rel_paths = []

    glob_pattern = os.path.join(seek_dir, pattern)
    for found_file in glob.glob(glob_pattern):
        # TODO: change name to BIDS name?
        filename = os.path.basename(found_file)
        shutil.copy(found_file, os.path.join(image_path, filename))
        rel_paths.append(rel_img_path(filename))

    return rel_paths


def find_and_copy_image(seek_dir, pattern, image_path):
    """
    Finds a file using pattern within the directory specified as
    seek_dir. If found, copies the file to the directory of images.

    :parameter: seek_dir: directory to be searched.
    :parameter: pattern: Unix shell pattern for finding files.
    :parameter: image_path: directory of images.
    :return: relative path to copied file, or None.
    """

    found_path = find_one_file(seek_dir, pattern)

    if found_path:
        # TODO: change name to BIDS name?
        # Copy the file to the path for the images.
        filename = os.path.basename(found_path)
        shutil.copyfile(found_path, os.path.join(image_path, filename))
        return rel_img_path(filename)

    else:
        return None


def find_one_file(seek_dir, pattern):

    one_file = None

    # Try to find a file with the pattern given in the directory given.
    glob_pattern = path.join(seek_dir, pattern)
    filelist = glob.glob(glob_pattern)

    # Make sure we got exactly one file.
    numfiles=len(filelist)
    if numfiles is 1:
        one_file = filelist[0]
    elif numfiles is not 0:
        # TODO: Log info in errorfile.
        print('\nFound %s files with pattern: %s' % (numfiles, glob_pattern))

    return one_file


def write_html(document, filename):
    """
    Writes an html document to a filename.

    :parameter: document: html document.
    :parameter: filename: name of html file.
    :return: None
    """
    try:
        f = open(filename, 'w')
        f.writelines(document)
        f.close()
        print('\nExecutive summary will be found in path:\n\t%s/%s' % (os.getcwd(), filename))
    except IOError:
        print('\ncannot write %s to %s for some reason...\n' % (filename, os.getcwd()))

class layout_builder(object):

    def __init__ (self, files_path, summary_path, html_path, subject_id, session_id, bids_path=None):

        self.working_dir = os.getcwd()

        self.files_path = files_path
        self.summary_path = summary_path
        self.html_path = html_path
        self.subject_id = subject_id
        self.session_id = session_id

        # Set up the paths at which to find image files.
        self.paths={}
        self.paths['proc'] = files_path
        self.paths['func'] = bids_path
        self.paths['summary'] = summary_path

        # We know we can write to the path.
        images_path = os.path.join(html_path, 'img')
        os.makedirs(images_path)

        # Use the relative path only, as the html will need to
        # access it's images using the relative path.
        self.images_path = os.path.relpath(images_path, html_path)

        # Copy the placeholders in case we cannot find a file.
        script_dir = os.path.dirname(os.path.realpath(__file__))
        program_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
        placeholder_dir = os.path.join(program_dir, 'placeholder_pictures')
        self.placeholders = {}
        self.placeholders['square'] = find_and_copy_image(placeholder_dir, 'square_placeholder_text.png', images_path)
        self.placeholders['rectangle'] = find_and_copy_image(placeholder_dir, 'rectangular_placeholder_text.png', images_path)

        self.setup()
        self.run()
        self.teardown()

    def setup(self):
        # As we write the html, we need to use the relative paths to the image
        # files that the html will reference. Therefore, best to be in the directory
        # to which the html will be written.
        os.chdir(self.html_path)
        print(os.getcwd())

    def teardown(self):
        # Go back to the path where we started.
        os.chdir(self.working_dir)
        print(os.getcwd())

    def run(self):
        # There are a bunch of scripts used in this page. Put them all together.
        scripts = BRAINSPRITE_SCRIPTS

        # Start building the html doc: put the subject ID into the title and page header.
        head = HTML_START
        head += TITLE % { 'subject': self.subject_id,
                          'session': self.session_id }

        body = ''
        # Make sections for T1 and T2 images. Includes slider for pngs and BrainSprite for each.
        t1_section, t1_scripts = make_tx_section('T1', self.summary_path, self.images_path)
        t2_section, t2_scripts = make_tx_section('T2', self.summary_path, self.images_path)
        body += t1_section + t2_section
        scripts += t1_scripts + t2_scripts

        # 'Combined' data for this subject/session: i.e., concatenated grayords and atlas images.
        body += make_combined_section(self.paths, self.placeholders, self.images_path)

        # Tasks section: data specific to each task/run.
        # Get a list of tasks processed for this subject.
        task_entries = image_summary.get_list_of_tasks(self.files_path)
        body += make_tasks_section(task_entries, self.paths, self.placeholders, self.images_path)

        # Assemble and write the document.
        html_doc = head + body + scripts + HTML_END
        write_html(html_doc, 'executive_summary_%s_%s.html' % (self.subject_id, self.session_id))



