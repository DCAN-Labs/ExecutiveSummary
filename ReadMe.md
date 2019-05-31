# Executive Summary

Executive Summary is intended as the last stage in any DCAN fMRI pipeline. It
is intended to show some key files to allow a quick QC of the image processing
results of a single session of a single subject. This program was designed along
with the DCAN fMRI pipelines, and depends upon their output. This is *not* a
stand-alone BIDS App.

The ```ExecutiveSummary.py``` script runs in 2 steps: preprocessing and layout
of the HTML page. The preprocessing step makes an ```executivesummary```
directory where the HTML file will eventually be written. It also makes an
```img``` subdirectory. The output from the preprocssing step is put into the
```img``` directory. For example, the preprocessor slices some of the BIDS input
(```nii.gz```) files into ```.png``` files; the ```.png``` output are stored in
```img```.
As of this writing, the files produced by the preprocessing step and stored in
```img``` do not have BIDS names.

You can move the Executive Summary output, to another directory (or device), but
it must be moved as a package. That is, the HTML must be in the same location as
the ```img``` directory so it can find its images.

### Requirements:
- Imaging Software Packages Required:
- fsl v4.1.9 or later
- workbench v1.3.2 or later
- Environment: python 3.7.x
- argparse
- PIL (Python Image Library)



### Usage:
* Executive Summary is run as a stage of the DCAN fMRI pipelines.
* Executive Summary can be run by passing the option ```--stage
 ExecutiveSummary``` to ```run.py```.
* ```ExecutiveSummary.py``` can be run from the command line as below:

 ```python
 usage: ExecutiveSummary.py [-h] --output-dir FILES_PATH [--bids-input FUNC_PATH]
                        --participant-label PARTICIPANT_LABEL
                        [--session-id SESSION_ID]
                        [--dcan-summary DCAN_SUMMARY] [--atlas ATLAS_PATH]
                        [--version] [--layout-only]

Builds the layout for the Executive Summary of the bids-formatted output from
the DCAN-Labs fMRI pipelines.

optional arguments:
  -h, --help            show this help message and exit
  --output-dir FILES_PATH, -o FILES_PATH
                        path to the output files directory for all
                        intermediate and output files from the pipeline. Path
                        should end with "files".
  --bids-input FUNC_PATH, -i FUNC_PATH
                        path to the bids dataset that was used as task input
                        to the pipeline. Path should end with "func"
  --participant-label PARTICIPANT_LABEL, -p PARTICIPANT_LABEL
                        participant label, not including "sub-".
  --session-id SESSION_ID, -s SESSION_ID
                        filter input dataset by session id. Default is all ids
                        found under each subject output directory(s). A
                        session id does not include "ses-"
  --dcan-summary DCAN_SUMMARY, -d DCAN_SUMMARY
                        Optional. Expects the name of the subdirectory used
                        for the summary data. Default:
                        summary_DCANBOLDProc_v4.0.0
  --atlas ATLAS_PATH, -a ATLAS_PATH
                        Optional. Expects the path to the atlas to register to
                        the images. Default:
                        templates/MNI_T1_1mm_brain.nii.gz.
  --version, -v         show version number and exit
  --layout-only         Can be specified for subjects that have been run
                        through the executivesummary preprocessor, so the
                        image data is ready. This calls only the
                        layout_builder to get the latest layout.
                        ```
