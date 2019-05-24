#! /usr/bin/env python

__doc__ = """
Builds the layout for the Executive Summary of the bids-formatted output from
the DCAN-Labs fMRI pipelines.
"""

__version__ = "2.0.0"

import os
from os import path
import re
import glob
from constants import *
from helpers import (find_one_file, find_and_copy_file, find_files, find_and_copy_files)


class ModalSlider(object):

    # Creates a modal container that contains a carousel
    # (aka slider), and a button to display the container.
    #
    # The slider will show each of the images in the list,
    # with its filename in the upper left, previous and
    # next buttons in the lower left and right respectively,
    # and a close button in the upper right.
    #
    # The image class must be unique to this slider so that
    # the scripts can find the images used by the slider.
    #
    # The modal id must be unique to this container, so that
    # buttons or clickable images or whatever, can display the
    # container.

    def __init__ (self, modal_id, image_class):
        self.modal_id = modal_id
        self.image_class = image_class
        self.image_class_idx = 0

        self.button = ''
        self.slider_scripts = ''
        self.modal_container = ''

    def get_id(self):
        return self.modal_id

    def get_image_class(self):
        return self.image_class

    def get_button(self):
        # Return the HTML that creates the button.
        return self.button


    def get_container(self):
        # Return the HTML that creates the container.
        return self.modal_container


    def get_scripts(self):
        return self.slider_scripts


    def open(self, btn_label):
        # Create the modal container.
        self.modal_container += MODAL_START % { 'modal_id' : self.modal_id }

        # Make a button to display the modal container.
        self.button += DISPLAY_MODAL_BUTTON.format( modal_id=self.modal_id, btn_label=btn_label )


    def add_images(self, image_list):
        # Add each image in the list to the slider.
        for image_file in image_list:
            self.add_image(image_file)


    def add_image(self, image_file):

        # Will display the name of the file on the image,
        # so get the filename by itself.
        image_name = os.path.basename(image_file)

        # Add the image to container, and assign the class.
        self.modal_container += IMAGE_WITH_NAME % {
                'image_class': self.image_class,
                'image_file' : image_file,
                'image_name' : image_name }
        self.image_class_idx += 1
        return self.image_class_idx


    def close(self):

        # Add the buttons at the end, so they don't
        # get hidden by the images.
        self.modal_container += MODAL_SLIDER_END % {
                'modal_id'   : self.modal_id,
                'image_class': self.image_class }

        # Close up all of the elements.
        self.slider_scripts += SLIDER_SCRIPTS % {
                'image_class': self.image_class }



class Section(object):
    def __init__ (self):
        self.section = ''
        self.scripts = ''

    def get_section(self):
        return self.section

    def get_scripts(self):
        return self.scripts


class TxSection(Section):

    def __init__ (self, tx, images_path):
        super(__class__, self).__init__()

        self.tx = tx
        self.images_path = images_path

        # As the images are added to the html, they are given a class. When the
        # script for the slider is called, it will allow the user to browse all
        # of the images of that class. Therefore, each slider must have its own
        # class. Use the same class throughout this instantiation.
        self.image_class = tx + 'pngs'

        # The modal container must be identified uniquely so that the correct
        # container is displayed with the correct button. Use this id throughout.
        self.modal_id = tx + '-modal'

        # Build everything.
        self.run()


    def make_brainsprite_viewer(self):
        """
        Builds HTML for BrainSprite viewer so users can click through 3d anatomical images.
        """
        spritelabel = ''
        spriteviewer = ''
        spriteloader = ''

        # Not all subjects have T1 and/or T2. See if we have data.
        mosaic_name = '%s_mosaic.jpg' % self.tx
        mosaic_path = os.path.join(self.images_path, mosaic_name)
        if os.path.isfile(mosaic_path):
            spritelabel += '<h6>BrainSprite Viewer: %s</h6>' % self.tx
            viewer = self.tx + '-viewer'
            spriteImg = self.tx + '-spriteImg'

            spriteviewer += SPRITE_VIEWER_HTML % {
                    'tx'         : self.tx,
                    'viewer'     : viewer,
                    'spriteImg'  : spriteImg,
                    'mosaic_path': mosaic_path,
                    'width'      : '100%' }

            spriteloader += SPRITE_LOAD_SCRIPT % {
                    'tx'        : self.tx,
                    'viewer'    : viewer,
                    'spriteImg' : spriteImg }

        return spritelabel, spriteviewer, spriteloader


    def run(self):
        # Make the brainsprite.
        brainsprite_label, brainsprite_viewer, brainsprite_loader = self.make_brainsprite_viewer ()

        # The pngs for the slider are already in the images_path. Get the pngs that start
        # with 'tx' so users can view the higher resolution pngs.
        pngs_glob = self.tx + '-*.png'
        pngs_list = sorted(find_files(self.images_path, pngs_glob))

        # Just a sanity check, since we happen to know how many to expect.
        if len(pngs_list) is not 9:
            print('Expected 9 %s pngs but found %s.' % (self.tx, len(pngs_list))) # TODO: log WARNING

        # Make a modal container with a slider and add the pngs.
        pngs_slider = ModalSlider(self.modal_id, self.image_class)
        pngs_slider.open('View %s pngs' % self.tx)
        pngs_slider.add_images(pngs_list)
        pngs_slider.close()

        # Add HTML for the bar with the brainsprite label and pngs button,
        # and for the brainsprite viewer.
        self.section += TX_SECTION % {
                'tx'                : self.tx,
                'brainsprite_label' : brainsprite_label,
                'pngs_button'       : pngs_slider.get_button(),
                'brainsprite_viewer': brainsprite_viewer }

        # HTML for the modal container should be tacked on the end.
        self.section += pngs_slider.get_container()

        self.scripts = brainsprite_loader + pngs_slider.get_scripts()


class AtlasSection(Section):

    def __init__ (self, img_in_path, img_out_path, regs_slider):
        super(__class__, self).__init__()

        # Super simple section: just one row of images.
        atlas_data = {}
        atlas_data['modal_id'] = regs_slider.get_id()

        for key in [ 'concat_pre_reg_gray', 'concat_post_reg_gray', 'atlas_in_t1', 't1_in_atlas' ]:
            values = IMAGE_INFO[key]
            pattern = values['pattern']
            img_file = find_and_copy_file(img_in_path, values['pattern'], img_out_path)
            if img_file is not None:
                atlas_data[key] = img_file
            else:
                atlas_data[key] = values['placeholder']

        # Add registration images to slider.
        idx = regs_slider.add_image(atlas_data['atlas_in_t1'])
        atlas_data['atlas_in_t1_idx'] = idx
        idx = regs_slider.add_image(atlas_data['t1_in_atlas'])
        atlas_data['t1_in_atlas_idx'] = idx

        # Write the HTML for the section.
        self.section += ATLAS_SECTION_START
        self.section += ATLAS_ROW.format(**atlas_data)
        self.section += ATLAS_SECTION_END

class TasksSection(Section):

    def __init__ (self, tasks, img_in_path, img_out_path, regs_slider):
        super(__class__, self).__init__()

        self.img_in_path = img_in_path
        self.img_out_path = img_out_path
        self.regs_slider = regs_slider

        self.run(tasks)

    def get_task_row_data(self, task_name, task_num):

        task_data = {}
        task_data['row_label'] = 'task-%s run-%s' % (task_name, task_num)
        task_data['modal_id'] = self.regs_slider.get_id()

        # Using glob patterns to find the files for this task; start
        # with a pattern for the task/run itself.
        task_pattern = task_name + '*' + task_num

        # For the processed files, it's as simple as looking for the pattern in
        # the source-directory. When found and copied to the directory of images,
        # add the file's path to the dictionary.
        for key in [ 'task_pre_reg_gray', 'task_post_reg_gray', 'task_in_t1', 't1_in_task' ]:
            values = IMAGE_INFO[key]
            pattern = values['pattern'] % task_pattern
            task_file = find_and_copy_file(self.img_in_path, pattern, self.img_out_path)
            if task_file:
                task_data[key] = task_file
            else:
                task_data[key] = values['placeholder']

        # Add registration images to slider.
        idx = self.regs_slider.add_image(task_data['task_in_t1'])
        task_data['task_in_t1_idx'] =idx
        idx = self.regs_slider.add_image(task_data['t1_in_task'])
        task_data['t1_in_task_idx'] =idx

        # These files should already be in the directory of images.
        for key in [ 'ref', 'bold' ]:
            values = IMAGE_INFO[key]
            pattern = values['pattern'] % task_pattern
            task_file = find_one_file(self.img_out_path, pattern)
            if task_file:
                task_data[key] = task_file
            else:
                task_data[key] = values['placeholder']

        return task_data


    def run(self, tasks):
        if len(tasks) is 0:
            print('No tasks were found.')
            return

        # Write the column headings.
        self.section += TASKS_SECTION_START

        # Each entry in task_entries is a tuple of the task-name (without
        # task-) and run number (without run-).
        for task_name, task_num in tasks:
            task_data = self.get_task_row_data(task_name, task_num)
            if task_data is not None:
                self.section += TASK_ROW.format(**task_data)

        # Add the end of the tasks section.
        self.section += TASKS_SECTION_END


class layout_builder(object):

    def __init__ (self, files_path, summary_path, html_path, images_path, subject_label, session_label):

        self.working_dir = os.getcwd()

        self.files_path = files_path
        self.summary_path = summary_path
        self.html_path = html_path
        self.subject_id = 'sub-' + subject_label
        self.session_id = 'ses-' + session_label

        # For the directory where the images used by the HTML are stored,  use
        # the relative path only, as the html will need to access it's images
        # using the relative path.
        self.images_path = os.path.relpath(images_path, html_path)

        self.setup()
        self.run()
        self.teardown()


    def setup(self):
        # As we write the HTML, we use the relative paths to the image files that
        # the HTML will reference. Therefore, best to be in the directory to which
        # the HTML will be written.
        os.chdir(self.html_path)


    def teardown(self):
        # Go back to the path where we started.
        os.chdir(self.working_dir)


    def get_list_of_tasks(self):
        # Walks through the MNINonLinear/Results directory to find all the
        # directories whose names contain 'task-'. This is the preferred
        # method. If there is no MNINonLinear/Results directory, uses the
        # files directory in the same way.

        taskset=set()

        use_path = os.path.join(self.files_path, 'MNINonLinear/Results')
        if os.path.isdir(use_path):
            print( '\nProcessed tasks will be found in path:\n\t%s' % use_path)
        else:
            use_path = self.files_path
            print( '\nProcessed tasks will be found in path:\n\t%s' % use_path)

        with os.scandir(use_path) as entries:
            for entry in entries:

                # Only worry about directories.
                if entry.is_dir():

                    # The name must match task- something. Ignore anything else.
                    # The name may contain other information  and it may or may not
                    # have '_run-' in it. For example:
                    #      ses-TWO_task-rest_run-01
                    #      task-rest01
                    # We want to capture the name of the task (word after 'task-'),
                    # lose anything between that name and the digits, and capture
                    # all of the digits:

                    task_re = re.compile('task-([^_\d]+)\D*(\d+).*')
                    match = task_re.search(entry.name)

                    if match is not None:
                        # Add this tuple to the set of tasks.
                        taskset.add(match.group(1,2))

        return sorted(taskset)


    def write_html(self, document, filename):
        """
        Writes an html document to a filename.

        :parameter: document: html document.
        :parameter: filename: name of html file.
        :return: None
        """
        filepath = os.path.join(os.getcwd(), filename)
        try:
            f = open(filepath, 'w')
        except OSError as err:
            print('Unable to open %s for write.\n' % filepath)
            print('Error: {0}'.format(err))

        f.writelines(document)
        print('\nExecutive summary can be found in path:\n\t%s/%s' % (os.getcwd(), filename))
        f.close()



    def run(self):

        # Start building the html document, and put the subject and session
        # into the title and page header.
        head = HTML_START
        head += TITLE % { 'subject': self.subject_id,
                          'session': self.session_id }
        body = ''
        # Make sections for 'T1' and 'T2' images. Include pngs slider and
        # BrainSprite for each.
        t1_section = TxSection('T1', self.images_path)
        t2_section = TxSection('T2', self.images_path)
        body += t1_section.get_section() + t2_section.get_section()

        # Images included in the Registrations slider are found in both
        # of the next 2 sections, so just create the ModalSlider now, and
        # add the files as we get them so they are in the proper order.
        regs_slider = ModalSlider('regsmodal', 'Registrations')
        regs_slider.open('View Registrations')

        # Data for this subject/session: i.e., concatenated grayords and atlas images.
        # (The atlas images will be added to the Registrations slider.)
        body += AtlasSection(self.summary_path, self.images_path, regs_slider).get_section()

        # Tasks section: data specific to each task/run. Get a list of tasks processed
        # for this subject. (The <task>-in-T1 and T1-in-<task> images will be added to
        # the Registrations slider.)
        task_list = self.get_list_of_tasks()
        body += TasksSection(task_list, self.summary_path, self.images_path, regs_slider).get_section()

        # Close up the Registrations elements; get the HTML.
        regs_slider.close()
        body += regs_slider.get_button()
        body += regs_slider.get_container()

        # There are a bunch of scripts used in this page. Keep them all together.
        scripts = BRAINSPRITE_SCRIPTS + t1_section.get_scripts() + t2_section.get_scripts() + regs_slider.get_scripts()

        # Assemble and write the document.
        html_doc = head + body + scripts + HTML_END
        self.write_html(html_doc, 'executive_summary_%s_%s.html' % (self.subject_id, self.session_id))



