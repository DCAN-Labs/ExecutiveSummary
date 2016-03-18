# Executive Summary 

## Program Launch:
### Call summary_tools/layout_builder.py from the command-line with -s and a path to processed data for one subject.
- wrap in a bash script for multiple subjects

## Requirements: 
- Software Packages: slicer, fsl, freesurfer
- Environment: python 2.7
- Folder Structure: 
  - /subject_with_processed_data/summary/
    - all .gif and .png images produced via FNL_PreProc: T1/T2 segmentations and coregistrations with functional
  - /subject_with_processed_data/summary/unprocessed/NIFTI
    - all _raw_ T1, T2, resting-state functional, and single-band reference data (nii or nii.gz) used in processing
    
## What It Makes:
- a sub-folder 'img' within /summary, containing:
    - new _.pngs_ of orthogonal slices for each raw and single-band reference, resting-state acquisitions
- _executive\_summary\_(code).html_: a layout of 4 panels for cursory quality assurance
    -  T1/T2 Structural Segmentation Slices Panel
    -  Parameter Table _(voxel dimensions, TR, TE, Number of Frames, Inversion Time)_
    -  Functional Data Panel _(raw and structurally registered image slices)_
    -  Concatenated Grayordinates Plot
  
## Summary Tools
### 1. layout_builder
        - launch via command-line, or within a shell-script, using -s and paths to subject folders
        - relies heavily upon functions in image_summary.py to build the layout components and extract parameters
### 2. image_summary
        - relies heavily upon mri_info, fslval, and slicer to extract data information and create new slices
        - contains lots of useful functions for flexibility

## Versions:
- layout_builder.py - v0.2.0
- image_summary.py - v0.2.0