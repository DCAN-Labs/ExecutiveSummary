# Executive Summary 

## Version: 

## Program Launch:
- from Linux: _python /PSYCH/code/release/executive_summary/summary_tools/layout_builder.py -s
/path/to/processed_subject_folder_ [-s /another/subject ... -s /another...]

## Requirements: 
- Software Packages that need to be installed on the system: slicer, fsl, freesurfer
- Environment: python 2.7
- Folder Structure: 
  - /subject_with_processed_data/summary/
    - all .gif and .png images produced via FNL_PreProc (_T1/T2 segmentations and coregistrations with functional_)
  - /subject_with_processed_data/summary/unprocessed/NIFTI
    - all _raw_ T1, T2, resting-state functional, and single-band reference data (nii or nii.gz) used in processing
  - /subject_with_processed_data/MNINonLinear
    
## What It Makes:
- a sub-folder 'img' within /summary, containing:
    - new _.pngs_ of orthogonal slices for each raw and single-band reference, resting-state acquisitions
- _executive\_summary\_(code).html_: a layout of 4 panels for cursory quality assurance
    -  T1/T2 Structural Segmentation Slices Panel
    -  Parameter Table _(voxel dimensions, TR, TE, Number of Frames, Inversion Time)_
    -  Functional Data Panel _(raw and structurally registered image slices)_
    -  Concatenated Grayordinates Plot

## File Structure:
## /summary_tools
### 1. layout_builder
   - launch via command-line, or within a shell-script, using -s and paths to subject folders
   - relies heavily upon functions in image_summary.py to build the layout components and extract parameters
### 2. image_summary
   - relies heavily upon mri_info, fslval, and slicer to extract data information and create new slices
## /helpers
### 1. shenanigans.py
   - various helper functions
## /TestCode
  - dispatch.py
  - table_template.html