# Executive Summary

## System Requirements
- Imaging Software Packages Required:
  - fsl v4.1.9 or later
  - freesurfer v5.3
- Environment: python 2.7.x
  - argparse
  - PIL (Python Image Library)

## Intended Usage
- run `layout_bulder.py` after FNL\_PreProc, but before any cleanup scripts have been run
- _Note: you can move the HTML to any other directory, but it needs its 'img' folder along with it to view the images!_

## Requirements for Processed and Raw Data Structures
- __FNL_PreProc MUST be completed!__
- Folder Structures:
  - /path/to/processed/pipeline/subjectID/summary/
     - .gif and .png images produced via FNL_PreProc (_T1/T2 segmentations or PNGs for BrainSprite, epi coregistrations with functional_)
  - /path/to/processed/pipeline/subjectID/unprocessed/NIFTI/
     - all __raw__ T1, T2, resting-state functional, and single-band reference data (nii or nii.gz) used in processing
  - /path/to/processed/pipeline/subjectID/MNINonLinear/Results/

### Expected naming convention for imaging data
  - Structural: `StudyName_SubjectID_T1w_MPR<series_num>.nii.gz`, `StudyName_SubjectID_T2w_SPC<series_num>.nii.gz`
  - for resting-state and SBRef: `StudyName_SubjectID_REST<series_num>_[SBRef].nii.gz`
  - e.g. _ABCDPILOT_MSC02_T1w_MPR1.nii.gz,  ABCDPILOT_MSC02_REST2\_SBRef.nii.gz,  ADHD-Youth\_1234-1\_REST3.nii.gz_

## Program Launch
- run `layout_builder.py` from appropriate local path
  - flags to add:
    - `-s /share/path/study/processed/subjID/visitID/pipeline/subjID/`
    - `[-s /another/subject ... -s /another...] `
    - `[-o /path/for/outputs/for_review]`
    - `[-v or -vv]`
    - `[--version]`
    - `[-h for help]`
    - `[--ica]`

## Outputs
- __executive\_summary\_(code).html__: a dashboard for cursory quality assurance
    -  BrainSprite viewer with clickable 3D images
    -  Parameter Table _(voxel dimensions, TR, TE, Number of Frames, Inversion Time)_
    -  Functional Data Panel _(raw and structurally registered image slices)_
    -  Concatenated Grayordinates Plots, pre-regression and post-regression, for entire run and for individual series
- a sub-directory 'img' (__/summary/img__), containing:
    - new _.pngs_ of orthogonally sliced image rows for each raw and single-band reference, resting-state acquisition series
    - copies of all _.gifs_ from /summary placed in inside the new /summary/img directory
    - new _.png_ images of each resting-state volume with othogonal slice-positions
- an output folder with copies of each summary requested for convenience
(__/summary/subjID_visitID__)
- some __\_log__ files for debugging

## Architecture
### /summary_tools
#### layout_builder.py
   - use -l and a path to a .txt file containing your subject-paths (single column)
   - use -s and paths to subject folders, separated by spaces
   - add -o </output/path> to control where the final product is copied
   - add --verbose for verbose output to _log file
   - add -vv for extra debugging output to _log file
   - use -h to print usage

#### image_summary.py
   - use -n to print parameters for any single nifti
   - use -d to print parameters for any single dicom
   - use --verbose for extra logging
   - use -vv to do even more logging
   - use -h to print usage

### /helpers
#### shenanigans.py
   - various helper functions

## Recent Updates
  - v1.5.0: Support for ABCD, monkey, and infant images, ica flag, pulling TE and TI from DICOMs
  - v1.3.0: add list-mode support! (supply a list of processed paths)
  - v1.2.3: floating points now have only 2 decimal places
  - v1.2.2: SBRef data can be found elsewhere when we do not have Raw

## Feature Requests
 - https://trello.com/b/R9xPDQNi/executive-summary-project

## Additional Documentation (under construction)
 - https://fair_lab.gitlab.io/executivesummary/index.html
