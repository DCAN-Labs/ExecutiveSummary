#! /usr/bin/env python

__doc__ = """
Builds the layout for the Executive Summary of the bids-formatted output from
the DCAN-Labs fMRI pipelines.
"""

__version__ = "2.0.0"

import os
from os import (path, getcwd, chmod, listdir)
import stat
import re
import glob
from constants import *
from helpers import (find_one_file, find_files, find_and_copy_files)


class ModalContainer(object):
    # Creates a modal container (with a close button), and
    # creates a button to display the container.
    #
    # A ModalContainer object must be created with these steps:
    #     1) Instantiate the object with an id and image class.
    #     2) Add the images to be shown in the container.
    #     3) Get the HTML for the container at the point in the
    #        document at which you want to insert the HTML.
    #
    # The steps are necessary so that buttons can be created
    # after all of the images have been added. Else, the images
    # hide the button.
    #
    # The modal id must be unique to this container, so that
    # buttons or clickable images or whatever, can display the
    # correct container.
    #
    def __init__ (self, modal_id, image_class):

        self.modal_id = modal_id
        self.modal_container = MODAL_START.format(modal_id=self.modal_id)
        self.button = ''

        self.image_class = image_class
        self.image_class_idx = 0

        self.scripts = ''

        self.state = 'open'


    def get_modal_id(self):
        return self.modal_id


    def get_image_class(self):
        return self.image_class


    def get_button(self, btn_label):
        # Return HTML to creates a button that displays the modal container.
        self.button += DISPLAY_MODAL_BUTTON.format(modal_id=self.modal_id, btn_label=btn_label)
        return self.button


    def get_container(self):
        # Add the close button after all images have been added (so
        # the button does not get covered by the image).
        self.state = 'closed'

        # Close up the elements.
        self.modal_container += MODAL_END.format(modal_id=self.modal_id)

        # Return the HTML.
        return self.modal_container


    def get_scripts(self):
        # The containter needs the scripts to show the correct
        # image when the container is opened.
        self.scripts += MODAL_SCRIPTS % {
                'modal_id'   : self.modal_id,
                'image_class': self.image_class }

        return self.scripts


    def add_images(self, image_list):
        # Add each image in the list to the slider.
        for image_file in image_list:
            self.add_image(image_file)

        # Return the final index.
        return self.image_class_idx


    def add_image(self, image_file):

        if self.state is not 'open':
            print('ERROR: Cannot add images after the HTML has been written.')
            return 0

        # Will display the name of the file on the image,
        # so get the filename by itself.
        display_name = os.path.basename(image_file)

        # Add the image to container, and assign the class.
        self.modal_container += IMAGE_WITH_CLASS.format(
                modal_id      = self.modal_id,
                image_class   = self.image_class,
                image_file    = image_file,
                display_name  = display_name)

        self.image_class_idx += 1
        return self.image_class_idx


class ModalSlider(ModalContainer):

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
    def __init__ (self, modal_id, image_class):
        ModalContainer.__init__(self, modal_id, image_class)


    def get_container(self):
        # Must add buttons after all images have been added.
        self.state = 'closed'

        # Add the buttons and close up the elements.
        self.modal_container += SLIDER_END.format(image_class=self.image_class)
        self.modal_container += MODAL_END.format(modal_id=self.modal_id)
        # Return the HTML.
        return self.modal_container


    def get_scripts(self):
        # The slider needs the scripts to go along with the
        # right and left buttons.
        self.scripts += SLIDER_SCRIPTS % {
                'modal_id'   : self.modal_id,
                'image_class': self.image_class }
        return self.scripts



class Section(object):
    def __init__ (self, img_path='./img', regs_slider=None, img_modal=None, **kwargs):
        self.section = ''
        self.scripts = ''
        self.img_path = img_path
        self.regs_slider = regs_slider
        self.img_modal = img_modal

    def get_section(self):
        return self.section

    def get_scripts(self):
        return self.scripts


class TxSection(Section):

    def __init__ (self, tx='', **kwargs):
        Section.__init__(self, **kwargs)

        self.tx = tx

        # As the images are added to the HTML, they are given a class. When the
        # script for the slider is called, it will allow the user to browse all
        # of the images of that class. Therefore, each slider must have its own
        # class. Use the same class throughout this instantiation.
        self.image_class = tx + 'pngs'

        # The modal container must be identified uniquely so that the correct
        # container is displayed with the correct button. Use this id throughout.
        self.modal_id = tx + '_modal'

        # Build everything.
        self.run()


    def make_brainsprite_viewer(self):
        # Builds HTML for BrainSprite viewer so users can click through 3d anatomical images.
        spritelabel = ''
        spriteviewer = ''
        spriteloader = ''

        # Not all subjects have T1 and/or T2. See if we have data.
        mosaic_name = '%s_mosaic.jpg' % self.tx
        mosaic_path = os.path.join(self.img_path, mosaic_name)
        if os.path.isfile(mosaic_path):
            # Insert the appropriate tx value in the ids, etc.
            spritelabel += '<h6>BrainSprite Viewer: %s</h6>' % self.tx
            viewer = self.tx + '-viewer'
            spriteImg = self.tx + '-spriteImg'

            spriteviewer += SPRITE_VIEWER_HTML.format(viewer=viewer, spriteImg=spriteImg,
                    mosaic_path=mosaic_path, width='100%')

            spriteloader += SPRITE_LOAD_SCRIPT % {
                    'tx'       : self.tx,
                    'viewer'   : viewer,
                    'spriteImg': spriteImg }

        return spritelabel, spriteviewer, spriteloader


    def run(self):
        # Make the brainsprite.
        brainsprite_label, brainsprite_viewer, brainsprite_loader = self.make_brainsprite_viewer ()

        # The pngs for the slider are already in the img_path. Get the pngs that start
        # with 'tx' so users can view the higher resolution pngs.
        pngs_glob = '*_' + self.tx + '-*.png'
        pngs_list = sorted(find_files(self.img_path, pngs_glob))

        # Just a sanity check, since we happen to know how many to expect.
        if len(pngs_list) is not 9:
            print('Expected 9 %s pngs but found %s.' % (self.tx, len(pngs_list))) # TODO: log WARNING

        # Make a modal container with a slider and add the pngs.
        pngs_slider = ModalSlider(self.modal_id, self.image_class)
        pngs_slider.add_images(pngs_list)

        # Add HTML for the bar with the brainsprite label and pngs button,
        # and for the brainsprite viewer.
        btn_label = 'View %s pngs' % self.tx
        self.section += TX_SECTION.format(tx=self.tx, brainsprite_label=brainsprite_label,
                pngs_button=pngs_slider.get_button(btn_label), brainsprite_viewer=brainsprite_viewer)

        # HTML for the modal container should be tacked on the end.
        self.section += pngs_slider.get_container()

        self.scripts = brainsprite_loader + pngs_slider.get_scripts()


class AnatSection(Section):

    def __init__ (self, img_path='./img', **kwargs):
        Section.__init__(self, **kwargs)

        self.img_path = img_path

        self.run()

    def write_atlas_rows(self):
        # Get images aligned with the atlas.
        atlas_data = {}
        atlas_data['regs_id'] = self.regs_slider.get_modal_id()

        for key in [ 'atlas_in_t1', 't1_in_atlas', 'atlas_in_subcort', 'subcort_in_atlas' ]:
            values = IMAGE_INFO[key]
            pattern = values['pattern']
            img_file = find_one_file(self.img_path, pattern)
            if img_file is not None:
                # Add image to data and to slider.
                atlas_data[key] = img_file
                atlas_data[key + '_idx'] = self.regs_slider.add_image(atlas_data[key])
            else:
                atlas_data[key] = values['placeholder']
                atlas_data[key + '_idx'] =  -1

        self.section += ATLAS_ROWS.format(**atlas_data)

    def write_gray_row(self):
        # Get gray-ordinates images.
        gray_data = {}
        gray_data['gray_id'] = self.img_modal.get_modal_id()

        for key in [ 'concat_pre_reg_gray', 'concat_post_reg_gray' ]:
            values = IMAGE_INFO[key]
            img_file = find_one_file(self.img_path, values['pattern'])
            if img_file is not None:
                gray_data[key] = img_file
                gray_data[key + '_idx'] = self.img_modal.add_image(gray_data[key])
                # Add image to data, and to the 'generic' images container.
            else:
                gray_data[key] = values['placeholder']
                gray_data[key + '_idx'] =  -1

        self.section += GRAY_ROW.format(**gray_data)

    def run(self):
        # Write the HTML for the section.
        self.section += ANAT_SECTION_START
        self.write_atlas_rows()
        self.write_gray_row()
        self.section += ANAT_SECTION_END


class TasksSection(Section):

    def __init__ (self, tasks=[], img_path='./img', **kwargs):
        Section.__init__(self, **kwargs)

        self.img_path = img_path

        self.run(tasks)

    def write_T1_reg_rows(self, task_name, task_num):
        t1_reg_data = {}
        t1_reg_data['row_label'] = 'task-%s run-%s' % (task_name, task_num)
        t1_reg_data['regs_id'] = self.regs_slider.get_modal_id()

        # Using glob patterns to find the files for this task; start
        # with a pattern for the task/run itself.
        task_pattern = task_name + '*' + task_num

        # For the processed files, it's as simple as looking for the pattern in
        # the source-directory. When found and copied to the directory of images,
        # add the file's path to the dictionary.
        for key in [ 'task_in_t1', 't1_in_task' ]:
            values = IMAGE_INFO[key]
            pattern = values['pattern'] % task_pattern
            task_file = find_one_file(self.img_path, pattern)
            if task_file:
                t1_reg_data[key] = task_file
                t1_reg_data[key + '_idx'] = self.regs_slider.add_image(t1_reg_data[key])
            else:
                t1_reg_data[key] = values['placeholder']
                t1_reg_data[key + '_idx'] =  -1

        self.section += T1_REG_ROWS.format(**t1_reg_data)

    def write_bold_gray_row(self, task_name, task_num):
        bold_data = {}
        bold_data['modal_id'] = self.img_modal.get_modal_id()

        # Using glob patterns to find the files for this task; start
        # with a pattern for the task/run itself.
        task_pattern = task_name + '*' + task_num

        # For gray files, there is only one name to look for.
        for key in [ 'task_pre_reg_gray', 'task_post_reg_gray' ]:
            values = IMAGE_INFO[key]
            pattern = values['pattern'] % task_pattern
            task_file = find_one_file(self.img_path, pattern)
            if task_file:
                bold_data[key] = task_file
                bold_data[key + '_idx'] = self.img_modal.add_image(bold_data[key])
            else:
                bold_data[key] = values['placeholder']
                bold_data[key + '_idx'] =  -1

        # For bold and ref files, may include run number or not.
        for key in [ 'bold', 'ref' ]:
            values = IMAGE_INFO[key]
            pattern = values['pattern'] % task_pattern
            task_file = find_one_file(self.img_path, pattern)
            if task_file:
                bold_data[key] = task_file
                bold_data[key + '_idx'] = self.img_modal.add_image(bold_data[key])
            else:
                # File was not found with both task name and run number.
                # Try again with task name only (no run number).
                pattern = values['pattern'] % task_name
                task_file = find_one_file(self.img_path, pattern)
                if task_file:
                    bold_data[key] = task_file
                    bold_data[key + '_idx'] = self.img_modal.add_image(bold_data[key])
                else:
                    bold_data[key] = values['placeholder']
                    bold_data[key + '_idx'] =  -1

        self.section += BOLD_GRAY_ROW.format(**bold_data)



    def run(self, tasks):
        if len(tasks) is 0:
            print('No tasks were found.')
            return

        # Write the column headings.
        self.section += TASKS_SECTION_START

        # Each entry in task_entries is a tuple of the task-name (without
        # task-) and run number (without run-).
        for task_name, task_num in tasks:
            self.write_T1_reg_rows(task_name, task_num)
            self.write_bold_gray_row(task_name, task_num)

        # Add the end of the tasks section.
        self.section += TASKS_SECTION_END


class layout_builder(object):

    def __init__ (self, files_path, summary_path, html_path, images_path, subject_id, session_id=None):

        self.working_dir = os.getcwd()

        self.files_path = files_path
        self.summary_path = summary_path
        self.html_path = html_path
        self.subject_id = 'sub-' + subject_id
        if session_id:
            self.session_id = 'ses-' + session_id
        else:
            self.session_id = None

        # For the directory where the images used by the HTML are stored,  use
        # the relative path only, as the HTML will need to access it's images
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
            print('\nProcessed tasks will be found in path:\n\t%s' % use_path)
        else:
            use_path = self.files_path
            print('\nProcessed tasks will be found in path:\n\t%s' % use_path)

        for name in os.listdir(use_path):

            # Only deal with subdirectories.
            pathname = os.path.join(use_path, name)
            if stat.S_ISDIR(os.stat(pathname).st_mode):

                # The name must match task- something. Ignore anything else.
                # The name may contain other information  and it may or may not
                # have '_run-' in it. For example:
                #      ses-TWO_task-rest_run-01
                #      task-rest01
                # We want to capture the name of the task (word after 'task-'),
                # lose anything between that name and the digits, and capture
                # all of the digits:

                task_re = re.compile('task-([^_\d]+)\D*(\d+).*')
                match = task_re.search(name)

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
            fd = open(filepath, 'w')
        except OSError as err:
            print('Unable to open %s for write.\n' % filepath)
            print('Error: {0}'.format(err))

        fd.writelines(document)
        print('\nExecutive summary can be found in path:\n\t%s/%s' % (os.getcwd(), filename))
        fd.close()



    def run(self):

        # Copy gray plot pngs, generated by DCAN-BOLD processing, to the
        # directory of images used by the HTML.
        find_and_copy_files(self.summary_path, '*DVARS_and_FD*.png', self.images_path)

        # Start building the HTML document, and put the subject and session
        # into the title and page header.
        head = HTML_START
        if self.session_id is None:
            head += TITLE.format(subject=self.subject_id, sep='' , session='')
        else:
            head += TITLE.format(subject=self.subject_id, sep=': ', session=self.session_id)
        body = ''

        # Images included in the Registrations slider and the Images container
        # are found in multiple sections. Create the objects now and add the files
        # as we get them.
        regs_slider = ModalSlider('regs_modal', 'Registrations')

        # Any image that is not shown in the sliders will be shown in a modal
        # container when clicked. Create that container now.
        img_modal = ModalContainer('img_modal', 'Images')

        # Some sections require more args, but most will need these:
        kwargs = { 'img_path'     : self.images_path,
                   'regs_slider'  : regs_slider,
                   'img_modal'    : img_modal }

        # Make sections for 'T1' and 'T2' images. Include pngs slider and
        # BrainSprite for each.
        t1_section = TxSection(tx='T1', **kwargs)
        t2_section = TxSection(tx='T2', **kwargs)
        body += t1_section.get_section() + t2_section.get_section()

        # Data for this subject/session: i.e., concatenated gray plots and atlas
        # images. (The atlas images will be added to the Registrations slider.)
        anat_section = AnatSection(**kwargs)
        body += anat_section.get_section()

        # Tasks section: data specific to each task/run. Get a list of tasks processed
        # for this subject. (The <task>-in-T1 and T1-in-<task> images will be added to
        # the Registrations slider.)
        tasks_list = self.get_list_of_tasks()
        tasks_section = TasksSection(tasks=tasks_list, **kwargs)
        body += tasks_section.get_section()

        # Close up the Registrations elements and get the HTML.
        body += img_modal.get_container() + regs_slider.get_container()

        # There are a bunch of scripts used in this page. Keep their HTML together.
        scripts = BRAINSPRITE_SCRIPTS + t1_section.get_scripts() + t2_section.get_scripts()
        scripts += img_modal.get_scripts() + regs_slider.get_scripts()

        # Assemble and write the document.
        html_doc = head + body + scripts + HTML_END
        if self.session_id is None:
            self.write_html(html_doc, 'executive_summary_%s.html' % (self.subject_id))
        else:
            self.write_html(html_doc, 'executive_summary_%s_%s.html' % (self.subject_id, self.session_id))



