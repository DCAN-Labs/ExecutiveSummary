#!/bin/bash

# Note: This file was copied from FNL_preproc_preproc.sh.
# It performs the steps needed to prep for exec summary. It does NOT call FNL_preproc.sh.

options=`getopt -o i:o:d:s:a:hx -l bids-input:,output-dir:,dcan-summary:,subject-id:,atlas:,help,skip_sprite -n 'executivesummary_preproc.sh' -- $@`
eval set -- "$options"
function display_help() {
    echo "Usage: `basename $0` [options...]                                                                           "
    echo "      Assumes BIDS & DCAN file structure, as follows:                                                       "
    echo "           <bids-input>/sub-<subject_id>/ses-<visit>/func                                                   "
    echo "           <output-dir>/sub-<subject_id>/ses-<visit>/files/<dcan-summary>                                   "
    echo "                                                                                                            "
    echo "      Required:                                                                                             "
    echo "      -i|--bids-input         Path to unprocessed data set, ending at func.                                 "
    echo "      -o|--output-dir         Path to processed files, ending at files.                                     "
    echo "      -d|--dcan-summary       Path to DCAN BOLD proc output, e.g. path to summary_DCANBOLDProc_v4.0.0.      "
    echo "      -s|--subject-id         Subject ID without sub- prefix.                                               "
    echo "                                                                                                            "
    echo "      Optional:                                                                                             "
    echo "      -a|--atlas              Atlas file for generation of rest image. Overrides MNI 1mm atlas.             "
    echo "      -h|--help               Display this message.                                                         "
    exit $1
}

echo "`basename $0` $options"
debug=0

# extract options and their arguments into variables.
while true ; do
    case "$1" in
        -i|--bids-input)
            bids_input="$2"
            shift 2
            ;;
        -o|--output-dir)
            output_dir="$2"
            shift 2
            ;;
        -d|--dcan-summary)
            dcan_summary="$2"
            shift 2
            ;;
        -s|--subject-id)
            subject_id="$2"
            shift 2
            ;;
        -a|--atlas)
            atlas="$2"
            shift 2
            ;;
        -x|--skip_sprite) # Stealth arg used only for debug.
            skip_sprite="skip"
            shift 1
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
echo bids-input=${bids_input}
echo output-dir=${output_dir}
echo dcan_summary=${dcan_summary}
echo subject_id=${subject_id}

if [[ ! -z ${skip_sprite} ]] ; then
    echo "Skipping sprite processing."
else
    echo "End of args"
fi

if [[ -z ${atlas} ]]; then
    echo Using default atlas.
    atlas=`dirname $0`/templates/MNI152_T1_1mm_brain.nii.gz
else
    echo Using atlas: $atlas
fi
echo

### SET UP ENVIRONMENT VARIABLES ###
# . `dirname $0`"/setup_env.sh"
if [ ! -z "${CARET7DIR}" ] ; then
    export wb_command=${CARET7DIR}/wb_command
fi

# TODO: lose this?
#if [ -z "${FSLDIR}" ] ; then
    FSLDIR='/usr/lib/fsl/5.0'
    FSL_DIR=${FSLDIR}
#fi

#matlab_template=`dirname $0`"/template_FNL_preproc_Matlab.m"

# Use the command line args to setup the requied paths
processed_files=${output_dir}
if [ -d ${processed_files} ]; then
    echo processed_files=${processed_files}
else
    echo "Directory does not exist: ${processed_files}" >&2
    display_help
    echo "Exiting." >&2
    exit
fi

# Note: we no longer *insist* that the summary file already exist, because if the subject is 'anatomy-only'
# there will be no files from DCAN_BOLD_proc. However, if there *are* any task files (including task-rest),
# this script will look for the .png files in the directory specified. Therefore, dcan_summary will
# *normally* be summary_DCANBOLDProc_v4.0.0.

if [ -d ${dcan_summary} ]; then
    echo Path to summary : ${dcan_summary}
else
    mkdir -p ${dcan_summary}
    chown :fnl_lab ${dcan_summary} || true
    chmod 770 ${dcan_summary} || true
fi

# Make the directory where we will store the HTML, and
# the directory to store its images.
exsum_path=${dcan_summary}/executivesummary
images_path=${exsum_path}/img

if ! [ -d ${images_path} ] ; then
    rm -rf ${images_path}
fi
mkdir -p ${images_path}

chown -R :fnl_lab ${exsum_path} || true
chmod -R 770 ${exsum_path} || true

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
        temp_scene=${processed_files}/image_template_temp.scene
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
        	temp_scene=${processed_files}/t1_169_scene.scene
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
			temp_scene=${processed_files}/t2_169_scene.scene
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
        temp_scene=${processed_files}/image_template_temp.scene
        echo "Calling wb_command as follows:"
        echo "      ${wb_command} -show-scene ${temp_scene} ${scenenum} ${out} 900 800 > /dev/null 2>&1"
        ${wb_command} -show-scene ${temp_scene} ${scenenum} ${out} 900 800 > /dev/null 2>&1

    }

    create_image_from_template_169() {

 		total_frames=169
		for ((i=1 ; i<=${total_frames} ;  i++)); do
            if [ "$1" -eq 1 ] ; then
                scene_file=${processed_files}/t1_169_scene.scene
                out=${dcan_summary}/T1_pngs/P_T1_frame_${i}.png
            elif [ "$1" -eq 2 ]; then
                scene_file=${processed_files}/t2_169_scene.scene
			    out=${dcan_summary}/T2_pngs/P_T2_frame_${i}.png
            fi
            echo $i
   			echo ${wb_command} -show-scene ${scene_file} ${i} ${out} 900 800
            ${wb_command} -show-scene ${scene_file} ${i} ${out} 900 800

        done
    }


################## BEGIN #########################

# If the bids-input was supplied and there are func files, slice
# the bold and sbrefs into pngs so we can display them.
shopt -s nullglob
if [ ! -z "${bids_input}" ] && [ -d ${bids_input} ] ; then

    # Slice bold.nii.gz files for tasks into pngs.
    bolds=( ${bids_input}/*task-*_bold*.nii* )
    for BOLD in ${bolds[@]} ; do
        png_name=$( basename ${BOLD} )
        png_name=${png_name/.nii.gz/.png}
        png_name=${png_name/.nii/.png}
        slicer ${BOLD} -u -a ${images_path}/${png_name}
    done

    # Slice sbref.nii.gz files for tasks into pngs.
    sbrefs=( ${bids_input}/*task-*_sbref*.nii* )
    count=${#sbrefs[@]}
    if (( 0 == count )) ; then
        # There are no SBRefs; use scout files for references.
        scouts=( ${processed_files}/*task-*/Scout_orig.nii.gz )
        for SCOUT in ${scouts[@]} ; do
            task_name=$(basename  $(dirname $SCOUT))
            png_name=${task_name}_ref.png
            slicer ${SCOUT} -u -a ${images_path}/${png_name}
        done
    else
        for SBREF in ${sbrefs[@]} ; do
            png_name=$( basename ${SBREF} )
            png_name=${png_name/.nii.gz/.png}
            png_name=${png_name/.nii/.png}
            slicer ${SBREF} -u -a ${images_path}/${png_name}
        done
    fi


fi
shopt -u nullglob

segBrain="wmparc.2.nii.gz"
segBrainDir="${processed_files}/MNINonLinear/ROIs"
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
t1_mask="${processed_files}/MNINonLinear/T1w_restore_brain.nii.gz"
if [[ ! -e ${atlas} ]] ; then
    echo "Missing ${atlas}"
    echo "Cannot create ${subject_id}_atlas_in_t1.gif or ${subject_id}_t1_in_atlas.gif."
else
    slices ${t1_mask} ${atlas} -o "${images_path}/${subject_id}_atlas_in_t1.gif"
    slices ${atlas} ${t1_mask} -o "${images_path}/${subject_id}_t1_in_atlas.gif"
fi

# From here on, use the whole T1 file rather than the mask (used above).
t1="${processed_files}/MNINonLinear/T1w_restore.nii.gz"
t2="${processed_files}/MNINonLinear/T2w_restore.nii.gz"
has_t2=1
if [[ ! -e ${t2} ]] ; then
    echo "t2 not found; using t1"
    has_t2=0
    t2="${t1}"
fi

rw="${processed_files}/MNINonLinear/fsaverage_LR32k/${subject_id}.R.white.32k_fs_LR.surf.gii"
rp="${processed_files}/MNINonLinear/fsaverage_LR32k/${subject_id}.R.pial.32k_fs_LR.surf.gii"
lw="${processed_files}/MNINonLinear/fsaverage_LR32k/${subject_id}.L.white.32k_fs_LR.surf.gii"
lp="${processed_files}/MNINonLinear/fsaverage_LR32k/${subject_id}.L.pial.32k_fs_LR.surf.gii"
t1_brain="${processed_files}/MNINonLinear/T1w_restore_brain.nii.gz"
t1_2_brain="${processed_files}/MNINonLinear/T1w_restore_brain.2.nii.gz"

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
        echo create_image_from_template "${images_path}/${image_names[$i]}.png" $scenenum
        create_image_from_template "${images_path}/${image_names[$i]}.png" $scenenum
    fi
done

rm -rf ${processed_files}/image_template_temp.scene

# Cannot do brain sprite processing if there is no template
if [[ ! -z ${skip_sprite} ]] ; then
    #skip brain sprite processing.
    echo Skipping brain sprite processing per user request.
elif [[ ! -e `dirname $0`/templates/parasagittal_Tx_169_template.scene ]] ; then
    echo Missing `dirname $0`/templates/parasagittal_Tx_169_template.scene
    echo Cannot perform processing needed for brainsprite.
elif [[ ${has_t2} -eq 1 ]] ; then
    #create brain sprite images for T1 and T2
    mkdir -p ${decan_summary}/T1_pngs/
    chown :fnl_lab ${decan_summary}/T1_pngs/ || true
    chmod 770 ${decan_summary}/T1_pngs/ || true
    mkdir -p ${decan_summary}/T2_pngs/
    chown :fnl_lab ${decan_summary}/T2_pngs/ || true
    chmod 770 ${decan_summary}/T2_pngs/ || true
    build_txw_scene_from_template_169 $t1 $rp $lp $rw $lw 1
    create_image_from_template_169 1
    build_txw_scene_from_template_169 $t2 $rp $lp $rw $lw 2
    create_image_from_template_169 2
else
    #create brain sprite images for T1 only
    mkdir -p ${decan_summary}/T1_pngs/
    chown :fnl_lab ${decan_summary}/T1_pngs/ || true
    chmod 770 ${decan_summary}/T1_pngs/ || true
    build_txw_scene_from_template_169 $t1 $rp $lp $rw $lw 1
    create_image_from_template_169 1
fi

if [[ -e ${t1_2_brain} ]] ; then
    echo "removing old resampled t1 brain"
    rm ${t1_2_brain}
fi

#make figures
for TASK in `ls -d ${processed_files}/*task-*` ; do
    fMRIName=`basename ${TASK}`
    echo "Making figures for TASK: ${TASK}"
    rest_img="${processed_files}/MNINonLinear/Results/${fMRIName}/${fMRIName}.nii.gz"
    #make t1 isovoxel brain with rest dim
    if [[ ! -e ${t1_2_brain} ]] ; then
        flirt -in ${t1_brain} -ref ${rest_img} -applyxfm -out ${t1_2_brain}
        echo result of flirt is in ${t1_2_brain}
    else
        echo failed: ${t1_2_brain} does not exist
    fi
    slices ${t1_2_brain} ${rest_img} -s 2 -o "${decan_summary}/${subject_id}_${fMRIName}_in_t1.gif"
    slices ${rest_img} ${t1_2_brain} -s 2 -o "${decan_summary}/${subject_id}_t1_in_${fMRIName}.gif"
done


echo "DONE: executive summary prep"

