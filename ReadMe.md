# Executive Summary

## Version: 1.0.2

## System Requirements:
- Software Packages Required: fsl (4.1.9 or later presumed), freesurfer (v5.3)
- Environment: python 2.7.x

## Processed and RAW Data Structures Required:
- FNL_PreProc MUST be completed
- Folder Structures:
  - /path/to/subjectID/summary/
    - .gif and .png images produced via FNL_PreProc (_T1/T2 segmentations and epi coregistrations with functional_)
  - /path/to/subjectID/unprocessed/NIFTI/
    - all _raw_ T1, T2, resting-state functional, and single-band reference data (nii or nii.gz) used in processing
  - /path/to/subjectID/MNINonLinear/Results/

## Program Launch:
- from Linux: _python /PSYCH/code/release/executive_summary/summary_tools/layout_builder.py -s /path/to/processed_subject_folder_ [-s /another/subject ... -s /another...]

## What It Makes:
- a sub-directory 'img' within /summary, containing:
    - new _.pngs_ of orthogonal slices for each raw and single-band reference, resting-state acquisition
    - copies of all .gifs from /summary placed in inside new ./img directory
- _executive\_summary\_(code).html_: a layout of 4 panels for cursory quality assurance
    -  T1/T2 Structural Segmentation Slices Panel
    -  Parameter Table _(voxel dimensions, TR, TE, Number of Frames, Inversion Time)_
    -  Functional Data Panel _(raw and structurally registered image slices)_
    -  Concatenated Grayordinates Plot
- some _log files for debugging

## Package Organization:
## /group_shares/PSYCH/code/release/utilities/executive_summary
## /summary_tools
### 1. layout_builder.py
   - launches via command-line, or within a shell-script, using -s and paths to subject folders, separated by spaces
   - relies heavily upon functions in image_summary.py to build the layout components and extract parameters
   - __e.g. python layout_builder.py -s /path/SUBJID_1/ -s /path/SUBJID_2__
### 2. image_summary.py
   - relies heavily upon mri_info, fslval, and slicer to extract data information and create new slices
## /helpers
### 1. shenanigans.py
   - various helper functions
## /TestCode
  - dispatch.py: used in testing, may disappear...
  - table_template.html: for viewing the Executive Summary layout in general
  - test_summary_airc.py: may delete this, but contains some simple tests

## Known Issues:
  - TE displayed as 0.00
  - image sizing for some raw data sets kinda small
  - extra zeroes in parameters panel rows

## Feature Requests
 - https://trello.com/b/R9xPDQNi/executive-summary-project