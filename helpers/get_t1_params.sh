#!/bin/bash

production_data_path_example='/group_shares/FAIR_HCP/HCP/processed/EEG-HumanAdult-OHSU/AIRC0001/20110826-SIEMENS-Nagel_K-Study/HCP_prerelease_FNL_0_1/MNINonLinear/Results/REST1'

test_data_path=$HOME/Projects/TestData/unprocessed/NIFTI

sub=11445-2
file_pat=${sub}_T1w_MPR?.nii.gz
files=$(ls $test_data_path/$file_pat)
num_files=$(echo $files | wc -w)

output=T1_params.txt
if [ -e $output ]; then mv ${output} ${output}.last_run; fi

echo "Modality,x,y,z,TE,TR,Frames,TI" >$output

for file in ${files[@]}; do 
	
	x=$(printf %.2f `fslval $file pixdim1`)
	y=$(printf %.2f `fslval $file pixdim2`)
	z=$(printf %.2f `fslval $file pixdim3`)
	frame_count=$(fslval $file dim4)  

	tr=$(printf %.2f `fslval $file pixdim4`)
	te=3.58  # need to pull from .dcm
	file_name_no_ext=$(basename $file .nii.gz)
	modality=${file_name_no_ext//${sub}_T1w_/}
	TI=900  # need to know where to pull

	echo "$modality,$x,$y,$z,$te,$tr,$frame_count,$TI" >>$output
done
