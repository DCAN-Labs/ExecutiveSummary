#!/bin/bash

# We should have lots of paths from the BIDS environment. If we are
# run from the command line, setup the one(s) we actually need.
if [ -z "${CARET7DIR}" ] ; then
    export CARET7DIR="/home/exacloud/lustre1/fnl_lab/code/external/utilities/workbench-1.3.2/bin_rh_linux64"
fi
export wb_command=${CARET7DIR}/wb_command

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

