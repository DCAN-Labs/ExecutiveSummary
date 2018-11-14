#!/bin/bash

FNL_preproc_dir=`dirname $0`
wb_command=${CARET7DIR}/wb_command

#    UTILITIES_DIR="/home/exacloud/lustre1/fnl_lab/code/internal/utilities"
#    FSL_DIR="/home/exacloud/lustre1/fnl_lab/code/bin/fsl/fsl"
#    path_to_label_files="/home/exacloud/lustre1/fnl_lab/ROI_sets/Surface_schemes/Human/"
#    Matlab_Runtime_Env="/home/exacloud/lustre1/fnl_lab/code/external/utilities/Matlab2016bRuntime/v91"
#    MCC_FILE=""
#    PMU_EXTRACT_DIR="/home/exacloud/lustre1/fnl_lab/code/internal/utilities/PMU_DICOM_extract"

#path_to_movment_regressor_check=${UTILITIES_DIR}/movmnt_regressor_check/movmnt_regressor_check.py
#framewise_disp_path=${UTILITIES_DIR}/framewise_displacement
#HCP_Mat_Path=${UTILITIES_DIR}/HCP_Matlab

#FSLDIR=${FSL_DIR}
#PATH=$FSLDIR/bin:$PATH
#export PATH FSLDIR
. ${FSLDIR}/etc/fslconf/fsl.sh

motion_filename="motion_numbers.txt"
skip_seconds=5
brain_radius_in_mm=50
expected_contiguous_frame_count=5

# frame displacement th to calculate beta coefficients for regression
fd_th=0.2

# Define filter parameters
bp_order=2 #band pass filter order
lp_Hz=0.009 # low pass frequency, Hz
hp_Hz=0.080 # high pass frequency, Hz

# Define constants
vent_lt_L=4 # white matter lower threshold Left
vent_ut_L=4 # white matter upper threshold Left
vent_lt_R=43 # white matter lower threshold Right
vent_ut_R=43 # white matter upper threshold Right

wm_lt_R=2950 # ventricles lower threshold Right
wm_ut_R=3050 # ventricles upper threshold Right
wm_lt_L=3950 # ventricles lower threshold Left
wm_ut_L=4050 # ventricles upper threshold Left


