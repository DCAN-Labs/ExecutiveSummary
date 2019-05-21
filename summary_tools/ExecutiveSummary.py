#! /usr/bin/env python

__doc__ = """
Builds the layout for the Executive Summary of the bids-formatted output from
the DCAN-Labs fMRI pipelines.
"""

__version__ = "2.0.0"

import os
from os import path
import argparse
import glob
import shutil
import subprocess
from layout_builder import layout_builder
from datetime import datetime


def generate_parser():

    parser = argparse.ArgumentParser(
            prog='ExecutiveSummary',
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter
            )
    parser.add_argument(
            'output_dir',
            help='path to the output directory for all intermediate and output '
            'files from the pipeline, also path in which logs are stored. Path '
            'should end at parent of sub- folder(s).'
            )
    parser.add_argument(
            '--version', '-v', action='version', version='%(prog)s ' + __version__
            )
    parser.add_argument(
            '--bids-input', '-i', dest='bids_dir',
            metavar='BIDS_INPUT',
            help='path to the bids dataset root directory that was used as '
             'input to the pipeline.'
            )
    parser.add_argument(
            '--participant-label', '-p', dest='subject_list',
            metavar='PARTICIPANT_LABEL', nargs='+',
            help='optional list of participant ids to run. Default is '
            'all ids found under the bids output directory. A participant '
            'label does not include "sub-"'
    )
    parser.add_argument(
            '--session-id', '-s', dest='session_list',
            metavar='SESSION_ID', nargs='+',
            help='filter input dataset by session id. Default is all ids '
            'found under each subject output directory(s). A session id '
            'does not include "ses-"'
    )
    parser.add_argument(
            '--dcan-summary', '-d', dest='summary_dir',
            metavar='DCAN_SUMMARY', default='summary_DCANBOLDProc_v4.0.0',
            help='Optional. Expects the name of the subdirectory used for the summary data. '
            'Default: summary_DCANBOLDProc_v4.0.0'
            )
    parser.add_argument(
            '--layout-only', dest='layout_only', action='store_true',
            help='Can be specified for subjects that have been run through the '
            'executivesummary preprocessor, so the image data is ready. This '
            'calls only the layout_builder to get the latest layout. '
            )

    return parser

def get_id_list(root_dir, prefix):
    """
    scan the root_dir for entries that are directories and
    that have the prefix indicated. Remove the prefix and
    return the entries.
    """
    idlist = []
    with os.scandir(root_dir) as entries:
        for entry in entries:
            if entry.name.startswith(prefix) and entry.is_dir():
                idlist.append(entry.name.replace(prefix, '', 1))

    return idlist

def init_subject(output_dir, bids_dir, subject_id):
    # Get the path to the subject's output.
    sub_out = os.path.join(output_dir, subject_id)
    if not os.path.isdir(sub_out):
        print('Directory does not exist: %s' % sub_out)
        return None, None

    # Get the path to the subject's input.
    if bids_dir is None:
        sub_in = None
    else:
        sub_in = os.path.join(bids_dir, subject_id)
        if not os.path.isdir(sub_in):
            sub_in = None

    return sub_out, sub_in


def init_session(sub_out, sub_in, session_id):

    proc_files = None
    func_files = None

    # Get the path to the session's output.
    ses_out = os.path.join(sub_out, session_id)
    proc_files = os.path.join(ses_out, 'files')
    if not os.path.isdir(proc_files):
        print('Directory does not exist: %s' % proc_files)
        return None, None

    # Get the path to the session's input.
    if sub_in is not None:
        # Some subjects have their bids input directly under
        # the subject's dir.
        func_files = os.path.join(sub_in, 'func')
        if not os.path.isdir(func_files):
            ses_in = os.path.join(sub_in, session_id)
            func_files = os.path.join(ses_in, 'func')
            if not os.path.isdir(func_files):
                func_files = None

    if func_files is None:
        print('\nPath to raw BIDS task data does not exist.\n\tPath: %s\nExiting....\n' % func_files)
    else:
        print('\nRaw BIDS task data will be found in path:\n\t%s' % func_files)

    return proc_files, func_files

def init_summary(proc_files, summary_dir):

    summary_path = None
    html_path = None

    summary_path = os.path.join(proc_files, summary_dir)
    if os.path.isdir(summary_path):
        # Build the directory tree for the output.
        # This also ensures we can write to the path.
        html_path = os.path.join(summary_path, 'executivesummary')

        if path.exists(html_path):
            shutil.rmtree(html_path, ignore_errors=True)

        try:
            os.makedirs(html_path)

        except OSError as err:
            print('cannot make executivesummary folder within path... permissions? \nPath: %s' % summary_path)
            print('OSError: %s' % err)
            summary_path = None
            html_path = None
    else:
        print('Directory does not exist: %s' % summary_dir)
        summary_path = None

    return summary_path, html_path


def _cli():
    """
    command line interface
    Parse all of the arguments and check for validity. Call the interface
    for one subject/session at a time (the way the pipeline would call it).
    :return:
    """
    parser = generate_parser()
    args = parser.parse_args()

    date_stamp = "{:%Y%m%d %H:%M}".format(datetime.now())

    print('Executive Summary was called at %s with:' % date_stamp)
    print('\tOutput directory:      %s' % args.output_dir)
    print('\tBIDS input files:      %s' % args.bids_dir)
    print('\tSubject list:          %s' % args.subject_list)
    print('\tSession list:          %s' % args.session_list)
    print('\tSummary directory:     %s' % args.summary_dir)

    # output_dir is required, and the parser would have squawked if there was
    # not a value for output_dir. Just make sure it's a real directory.
    assert os.path.isdir(args.output_dir), args.output_dir + ' is not a directory!'

    # bids_dir is not required for Executive Summary. If not there, will just not
    # have any raw data (SBRef or BOLD) in the output for each task. If supplied,
    # just make sure it's a real directory.
    if args.bids_dir is not None:
        assert os.path.isdir(args.bids_dir), args.bids_dir + ' is not a directory!'

    # Find all entries under args.output_dir.
    subjects = get_id_list(args.output_dir, 'sub-')

    # Filter by subject_list.
    if isinstance(args.subject_list, list):
        subjects = [s for s in subjects if s in args.subject_list]


    # Put together the arguments for one subject at a time.
    for subject_label in subjects:
        subject_id = 'sub-' + subject_label
        sub_out, sub_in = init_subject(args.output_dir, args.bids_dir, subject_id)

        # Each subject must have already been through the DCAN
        # pipeline, and we must have a valid output directory
        # in order to process the subject.
        if sub_out is None:
            print('Skipping %s.' % (subject_id))
            continue


        # Find all sessions under subdir.
        sessions = get_id_list(sub_out, 'ses-')

        # Filter by session_list.
        if isinstance(args.session_list, list):
            sessions = [s for s in sessions if s in args.session_list]

        # Loop throught the sessions.
        for session_label in sessions:
            session_id = 'ses-' + session_label
            proc_files, func_files = init_session(sub_out, sub_in, session_id)

            # We must have a valid output directory in order to
            # process the subject/session.
            if proc_files is None:
                print('Skipping %s, %s' % (subject_id, session_id))
                continue

            if func_files is None:
                print('No raw data will be shown for %s, %s' % (subject_id, session_id))

            # Most of the data is in the summary directory. Also, it is
            # where the layout_builder will write the html.
            summary_path, html_path = init_summary(proc_files, args.summary_dir)
            if summary_path is None:
                print('Skipping %s, %s' % (subject_id, session_id))
                continue

            # All of the args for this subject/session pass muster. Call the interface.
            kwargs = {
                'files_path'   : proc_files,
                'summary_path' : summary_path,
                'html_path'    : html_path,
                'subject_id'   : subject_id,
                'session_id'   : session_id,
                'bids_path'    : func_files,
                'layout_only'  : args.layout_only
                }

    return interface(**kwargs)

def interface(files_path, summary_path, html_path, subject_id, session_id, bids_path=None, layout_only=False):

    if not layout_only:
        # TODO: will eventually call the preprocessing step from inside the interface so there is only ONE ExecSumm app.
        wrapper_cmd = 'executivesummary_wrapper.sh files_path=%s summary_path=%s subject_id=%s session_id=%s bids_path=%s'
        print ('KJS: would now call wrapper with cmd:\n\t%s' % wrapper_cmd)

    kwargs = {
        'files_path'   : files_path,
        'summary_path' : summary_path,
        'html_path'    : html_path,
        'subject_id'   : subject_id,
        'session_id'   : session_id,
        'bids_path'    : bids_path
        }

    #layout_builder.interface(**kwargs)
    layout_builder(**kwargs)

if __name__ == '__main__':

    _cli()
    print('\nall done!')
