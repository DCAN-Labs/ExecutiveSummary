# Executive Summary v1.0.2

## System Requirements:
- Imaging Software Packages Required: 
  - fsl v4.1.9 or later
  - freesurfer v5.3
- Environment: python 2.7.x 
  - argparse
  
## Intended Usage:
- run `layout_bulder.py` after FNL\_PreProc, but before any cleanup scripts have been ran
- _Note: you can move the HTML to any other directory, but it needs its 'img' folder along with it to view the images!_

## Processed and RAW Data Structures Required:
- FNL_PreProc MUST be completed
- Folder Structures:
  - /path/to/processed/pipeline/subjectID/summary/
    - .gif and .png images produced via FNL_PreProc (_T1/T2 segmentations and epi coregistrations with functional_)
  - /path/to/processed/pipeline/subjectID/unprocessed/NIFTI/
    - all _raw_ T1, T2, resting-state functional, and single-band reference data (nii or nii.gz) used in processing
  - /path/to/processed/pipeline/subjectID/MNINonLinear/Results/

## Program Launch:
- from any beast or qlogin-session to the AIRC, open a terminal and enter: 
  `python /PSYCH/code/release/executive_summary/summary_tools/layout_builder.py -s </path/to/processed/pipeline/subjectID/>  [ -s /another/subject ... -s /another...]`

## What It Makes:
- a sub-directory 'img' (/summary/img):
    - new _.pngs_ of orthogonally sliced image rows for each raw and single-band reference, resting-state acquisition series
    - copies of all .gifs from /summary placed in inside a new ./img directory, within the /summary directory
    - new _.png_ images of each resting-state volume with othogonal slice-positions in regions known to be affected by susceptibility artifacts, or other issues that commonly occur during processing
- _executive\_summary\_(code).html_: a layout of 4 panels for cursory quality assurance
    -  T1/T2 Structural Segmentation Slices Panel
    -  Parameter Table _(voxel dimensions, TR, TE, Number of Frames, Inversion Time)_
    -  Functional Data Panel _(raw and structurally registered image slices)_
    -  Concatenated Grayordinates Plot
- some _\_log_ files for debugging

## Package Organization:
## /group_shares/PSYCH/code/release/utilities/executive_summary
## /summary_tools
### 1. layout_builder.py
   - launches via command-line, or within a shell-script, using -s and paths to subject folders, separated by spaces 
   
### 2. image_summary.py
   - relies heavily upon mri_info, fslval, and slicer to extract data and create new .png slices
   
## /helpers
### 1. shenanigans.py
   - various helper functions, some are used, some are place-holders 
  
## /TestCode
  - table_template.html: Executive Summary mock-up
  - dispatch.py: used in testing, may disappear...
  - test_summary_airc.py: may delete this, but contains some simple tests

## Known Issues:
  - TE displayed as 0.00
  - image sizing for some raw data sets may be small and require zooming-in on your browser to view
  - non-significant zeroes in some parameters panel rows
  - TI displayed as 1 for all modalities

## Feature Requests
 - https://trello.com/b/R9xPDQNi/executive-summary-project