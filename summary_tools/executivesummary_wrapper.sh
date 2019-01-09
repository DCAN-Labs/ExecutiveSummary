#!/bin/bash

# Note: This file was copied from FNL_preproc_wrapper.sh.
# It performs the steps needed to prep for exec summary. It does NOT call FNL_preproc.sh.

options=`getopt -o u:d:s:e:o:h:a:x -l unproc_root:,deriv_root:,subject_id:,,ex_summ_dir:,output_path:,skip_sprite:,atlas:,help: -n 'executive_summary_prep.sh' -- $@`
eval set -- "$options"
function display_help() {
    echo "Usage: `basename $0` [options...] "
    echo "      Assumes BIDS & DCAN file structure, as follows:"
    echo "           <unproc_root>/sub-<subject_id>/ses-<visit>/func"
    echo "           <deriv_root>/sub-<subject_id>/ses-<visit>/files/<ex_summ_dir>"
    echo " "
    echo "      Required:"
    echo "      -u|--unproc_root        Path to unprocessed data set, ending 'func' or 'anat' or whatever."
    echo "      -d|--deriv_root         Path to derivatives files, ending at files. "
    echo "      -s|--subject_id         Subject ID without sub- prefix"
    echo "      -e|--ex_summ_dir        Executive summary subdirectory, for example: summary_DCANBOLDProc_v4.0.0 "
    echo " "
    echo "      Optional:"
    echo "      -o|--output_path        Path to a writable directory where a copy of the output will be placed "
    echo "      -a|--atlas              atlas file for generation of rest image. Overrides MNI 1mm atlas"
    echo "      -h|--help               Display this message"
    exit $1
}

echo "`basename $0` $options"
debug=0

# extract options and their arguments into variables.
while true ; do
    case "$1" in
        -u|--unproc_root)
            unproc_root="$2"
            shift 2
            ;;
        -d|--deriv_root)
            deriv_root="$2"
            shift 2
            ;;
        -s|--subject_id)
            subject_id="$2"
            shift 2
            ;;
        -e|--ex_summ_dir)
            ex_summ_dir="$2"
            shift 2
            ;;
        -o|--output_path)
            output_path="$2" # Not used until we call layout_buider.py at end of script.
            shift 2
            ;;
        -x|--skip_sprite) # Stealth arg used only for debug.
            skip_sprite="skip"
            shift 1
            ;;
        -a|--atlas)
            atlas="$1"
            shift 2
            ;;
        -h|--help)
            display_help;;
        --) shift ; break ;;
        *) echo "Unexpected error parsing args!" ; display_help 1 ;;
    esac
done


# Check that each of the required args is there (?)
echo
echo "COMMAND LINE ARGUMENTS:"
echo unproc_root=${unproc_root?}
echo deriv_root=${deriv_root?}
echo subject_id=${subject_id?}
echo ex_summ_dir=${ex_summ_dir?}
if [[ ! -z ${output_path} ]] ; then
    echo output_path=${output_path}
fi
if [[ ! -z ${skip_sprite} ]] ; then
    echo "Skipping sprite processing."
else
    echo "End of args"
fi
if [[ -z ${atlas} ]]; then
    atlas=`dirname $0`/templates/MNI152_T1_1mm_brain.nii.gz
fi
echo

### SET UP ENVIRONMENT VARIABLES ###
# . `dirname $0`"/setup_env.sh"
export wb_command=${CARET7DIR}/wb_command

#matlab_template=`dirname $0`"/template_FNL_preproc_Matlab.m"

# Use the command line args to setup the requied paths
ProcessedFiles="${deriv_root}"
if [ -d ${ProcessedFiles} ]; then
    echo ProcessedFiles=${ProcessedFiles}
else
    echo "Directory of derivatives does not exist: ${ProcessedFiles}" >&2
    display_help
    echo "Exiting." >&2
    exit
fi

UnprocessedFiles="${unproc_root}"
if [ -d ${UnprocessedFiles} ]; then
    echo UnprocessedFiles=${UnprocessedFiles}
else
    echo "Directory of unprocessed data does not exist: ${UnprocessedFiles}" >&2
    display_help
    echo "Exiting." >&2
    exit
fi

# The summary subdirectory must alread exist, since DCANBOLDProc must already have been run.
ExSummPath="${ProcessedFiles}/${ex_summ_dir}/"
if [ -d ${ExSummPath} ]; then
    echo Path to summary : ${ExSummPath}
else
    echo "Summary directory does not exist: ${ExSummPath}" >&2
    display_help
    echo "Make sure all required pre-processing has been run." >&2
    echo "Exiting." >&2
    exit
fi

############ HELPER FUNCTIONS ##############

    # Prints the error message and the line of code, where the error occurred; then Exits the script.
    print_error() {
        local msg="$1"
        local err_code="${2:-1}"
        read line file <<<$(caller)
        echo "An ERROR occurred in line $line of file $file." >&2
        if [[ -n "$msg" ]]; then
            echo ${msg} >&2
        fi

        exit ${err_code}
    }
    trap 'print_error' ERR

    #takes the following arguments: t2_path t1_path rp_path lp_path rw_path lw_path
    build_scene_from_template(){
        temp_scene=${ProcessedFiles}/image_template_temp.scene
        cp `dirname $0`/templates/image_template_temp.scene $temp_scene

        declare -a templates=('T2_IMG' 'T1_IMG' 'RPIAL' 'LPIAL' 'RWHITE' 'LWHITE')
        declare -a paths=($1 $2 $3 $4 $5 $6)

        for i in `seq 0 5`;
        do
            #replace templated pathnames and filenames in scene
            sed -i "s!${templates[$i]}_PATH!${paths[$i]}!g" $temp_scene
            filename=$(basename "${paths[$i]}")
            sed -i "s!${templates[$i]}_NAME!${filename}!g" $temp_scene
        done
    }

    build_txw_scene_from_template_169(){
        if [ "$6" -eq 1 ] ; then
        	temp_scene=${ProcessedFiles}/t1_169_scene.scene
            cp `dirname $0`/templates/parasagittal_Tx_169_template.scene $temp_scene

            declare -a templates=('TX_IMG' 'R_PIAL' 'L_PIAL' 'R_WHITE' 'L_WHITE')
            declare -a paths=($1 $2 $3 $4 $5)

            for i in `seq 0 4`; do
            	#replace templated pathnames and filenames in scene
                echo sed -i "s!${templates[$i]}_NAME_and_PATH!${paths[$i]}!g" $temp_scene
            	sed -i "s!${templates[$i]}_NAME_and_PATH!${paths[$i]}!g" $temp_scene
                filename=$(basename "${paths[$i]}")
                echo sed -i "s!${templates[$i]}_NAME!${filename}!g" $temp_scene
                sed -i "s!${templates[$i]}_NAME!${filename}!g" $temp_scene
           	done

        elif [ "$6" -eq 2 ] ; then
			temp_scene=${ProcessedFiles}/t2_169_scene.scene
            cp `dirname $0`/templates/parasagittal_Tx_169_template.scene $temp_scene

            declare -a templates=('TX_IMG' 'R_PIAL' 'L_PIAL' 'R_WHITE' 'L_WHITE')
            declare -a paths=($1 $2 $3 $4 $5)

            for i in `seq 0 4`; do
            	#replace templated pathnames and filenames in scene
            	sed -i "s!${templates[$i]}_NAME_and_PATH!${paths[$i]}!g" $temp_scene
            	filename=$(basename "${paths[$i]}")
            	sed -i "s!${templates[$i]}_NAME!${filename}!g" $temp_scene
        	done
	fi
    }

    #takes the following arguments: out_path scenenum
    create_image_from_template() {
        out=$1
        scenenum=$2
        temp_scene=${ProcessedFiles}/image_template_temp.scene
        echo "Calling wb_command as follows:"
        echo "      ${wb_command} -show-scene ${temp_scene} ${scenenum} ${out} 900 800 > /dev/null 2>&1"
        ${wb_command} -show-scene ${temp_scene} ${scenenum} ${out} 900 800 > /dev/null 2>&1

    }

    create_image_from_template_169() {

 		total_frames=169
		for ((i=1 ; i<=${total_frames} ;  i++)); do
            if [ "$1" -eq 1 ] ; then
                scene_file=${ProcessedFiles}/t1_169_scene.scene
                out=${ExSummPath}/T1_pngs/P_T1_frame_${i}.png
            elif [ "$1" -eq 2 ]; then
                scene_file=${ProcessedFiles}/t2_169_scene.scene
			    out=${ExSummPath}/T2_pngs/P_T2_frame_${i}.png
            fi
            echo $i
   			echo ${wb_command} -show-scene ${scene_file} ${i} ${out} 900 800
            ${wb_command} -show-scene ${scene_file} ${i} ${out} 900 800

        done
    }


################## BEGIN #########################

segBrain="wmparc.2.nii.gz"
segBrainDir="${ProcessedFiles}/MNINonLinear/ROIs"
wm_mask_L="L_wm_2mm_${subject_id}_mask.nii.gz"
wm_mask_R="R_wm_2mm_${subject_id}_mask.nii.gz"
wm_mask="wm_2mm_${subject_id}_mask.nii.gz"
wm_mask_eroded="wm_2mm_${subject_id}_mask_erode.nii.gz"
vent_mask_L="L_vent_2mm_${subject_id}_mask.nii.gz"
vent_mask_R="R_vent_2mm_${subject_id}_mask.nii.gz"
vent_mask="vent_2mm_${subject_id}_mask.nii.gz"
vent_mask_eroded="vent_2mm_${subject_id}_mask_eroded.nii.gz"

echo
echo "START: executive summary"

#Should we use $FSLDIR/data/standard instead of ./templates??
t1_mask="${ProcessedFiles}/MNINonLinear/T1w_restore_brain.nii.gz"
if [[ ! -e ${atlas} ]] ; then
    echo "Missing ${atlas}"
    echo "Cannot create ${subject_id}_atlas_in_t1.gif or ${subject_id}_t1_in_atlas.gif."
else
    slices ${t1_mask} ${atlas} -o "${ExSummPath}/${subject_id}_atlas_in_t1.gif"
    slices ${atlas} ${t1_mask} -o "${ExSummPath}/${subject_id}_t1_in_atlas.gif"
fi

# From here on, use the whole T1 file rather than the mask (used above).
t1="${ProcessedFiles}/MNINonLinear/T1w_restore.nii.gz"
t2="${ProcessedFiles}/MNINonLinear/T2w_restore.nii.gz"
has_t2=1
if [[ ! -e ${t2} ]] ; then
    echo "t2 not found; using t1"
    has_t2=0
    t2="${t1}"
fi

rw="${ProcessedFiles}/MNINonLinear/fsaverage_LR32k/${subject_id}.R.white.32k_fs_LR.surf.gii"
rp="${ProcessedFiles}/MNINonLinear/fsaverage_LR32k/${subject_id}.R.pial.32k_fs_LR.surf.gii"
lw="${ProcessedFiles}/MNINonLinear/fsaverage_LR32k/${subject_id}.L.white.32k_fs_LR.surf.gii"
lp="${ProcessedFiles}/MNINonLinear/fsaverage_LR32k/${subject_id}.L.pial.32k_fs_LR.surf.gii"
t1_brain="${ProcessedFiles}/MNINonLinear/T1w_restore_brain.nii.gz"
t1_2_brain="${ProcessedFiles}/MNINonLinear/T1w_restore_brain.2.nii.gz"

#create summary images
build_scene_from_template $t2 $t1 $rp $lp $rw $lw
declare -a image_names=('T1-Axial-InferiorTemporal-Cerebellum' 'T2-Axial-InferiorTemporal-Cerebellum' 'T1-Axial-BasalGangila-Putamen' 'T2-Axial-BasalGangila-Putamen' 'T1-Axial-SuperiorFrontal' 'T2-Axial-SuperiorFrontal' 'T1-Coronal-PosteriorParietal-Lingual' 'T2-Coronal-PosteriorParietal-Lingual' 'T1-Coronal-Caudate-Amygdala' 'T2-Coronal-Caudate-Amygdala' 'T1-Coronal-OrbitoFrontal' 'T2-Coronal-OrbitoFrontal' 'T1-Sagittal-Insula-FrontoTemporal' 'T2-Sagittal-Insula-FrontoTemporal' 'T1-Sagittal-CorpusCallosum' 'T2-Sagittal-CorpusCallosum' 'T1-Sagittal-Insula-Temporal-HippocampalSulcus' 'T2-Sagittal-Insula-Temporal-HippocampalSulcus')
((num_wb_scenes=${#image_names[@]}-1))

for i in `seq 0 ${num_wb_scenes}`;
do
    ((scenenum=(i+1)))

    if [[ ${has_t2} -eq 0 && $(( $scenenum % 2 )) -eq 0 ]] ; then
        echo "skipping t2 image"
    else
        create_image_from_template "${ExSummPath}/${image_names[$i]}.png" $scenenum
        echo create_image_from_template "${ExSummPath}/${image_names[$i]}.png" $scenenum
    fi
done

rm -rf ${ProcessedFiles}/image_template_temp.scene

# Cannot do brain sprite processing if there is no template
if [[ ! -e `dirname $0`/templates/parasagittal_Tx_169_template.scene ]] ; then
    echo Missing `dirname $0`/templates/parasagittal_Tx_169_template.scene
    echo Cannot perform processing needed for brainsprite.
elif [[ ! -z ${skip_sprite} ]] ; then
    #skip brain sprite processing.
    echo Skipping brain sprite processing per user request.
elif [[ ${has_t2} -eq 1 ]] ; then
    #create brain sprite images for T1 and T2
    mkdir -p ${ExSummPath}/T1_pngs/
    mkdir -p ${ExSummPath}/T2_pngs/
    build_txw_scene_from_template_169 $t1 $rp $lp $rw $lw 1
    create_image_from_template_169 1
    build_txw_scene_from_template_169 $t2 $rp $lp $rw $lw 2
    create_image_from_template_169 2
else
    #create brain sprite images for T1 only
    mkdir -p ${ExSummPath}/T1_pngs/
    build_txw_scene_from_template_169 $t1 $rp $lp $rw $lw 1
    create_image_from_template_169 1
fi

if [[ -e ${t1_2_brain} ]] ; then
    echo "removing old resampled t1 brain"
    rm ${t1_2_brain}
fi

#make figures
for TASK in `ls -d ${ProcessedFiles}/*task-*` ; do
    fMRIName=`basename ${TASK}`
    echo "Making figures for TASK: ${TASK}"
    rest_img="${ProcessedFiles}/MNINonLinear/Results/${fMRIName}/${fMRIName}.nii.gz"
    #make t1 isovoxel brain with rest dim
    if [[ ! -e ${t1_2_brain} ]] ; then
        flirt -in ${t1_brain} -ref ${rest_img} -applyxfm -out ${t1_2_brain}
        echo result of flirt is in ${t1_2_brain}
    else
        echo failed: ${t1_2_brain} does not exist
    fi
    slices ${t1_2_brain} ${rest_img} -s 2 -o "${ExSummPath}/${subject_id}_${fMRIName}_in_t1.gif"
    slices ${rest_img} ${t1_2_brain} -s 2 -o "${ExSummPath}/${subject_id}_t1_in_${fMRIName}.gif"
done

echo "DONE: executive summary prep"
echo
date
echo
echo "Entering layout of html file."
echo
echo "Parameters to layout_builder.py: "
echo "--unproc_root=" ${unproc_root}
echo "--deriv_root=" ${deriv_root}
echo "--subject_id=" ${subject_id}
echo "--ex_summ_dir=" ${ex_summ_dir}
echo "--output_path=" ${output_path}
echo

if [[ -z ${output_path} ]] ; then
    `dirname $0`/layout_builder.py \
          --unproc_root="${unproc_root}" \
          --deriv_root="${deriv_root}" \
          --subject_id="${subject_id}" \
          --ex_summ_dir="${ex_summ_dir}"
else
    `dirname $0`/layout_builder.py \
          --unproc_root="${unproc_root}" \
          --deriv_root="${deriv_root}" \
          --subject_id="${subject_id}" \
          --ex_summ_dir="${ex_summ_dir}" \
          --output_path="${output_path}"
fi

echo "DONE: executive_summary"

