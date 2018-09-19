#!/bin/bash 

# Note: This file was copied from FNL_preproc_wrapper.sh. 
# It performs the steps needed to prep for exec summary. It does NOT call FNL_preproc.sh.

options=`getopt -o p:n:i:v:e:h -l path:,name:,id:,visit:,ex-folder:,help -n 'executive_summary_prep.sh' -- $@`
eval set -- "$options"
function display_help() {
    echo "Usage: `basename $0` [options...] "
    echo "      Assumes BIDS file structure, as follows:"
    echo "           <path_to_data=>/HCP/[processed,sorted]/<study_name>/sub-<subject_id>/ses-<visit>/files/<ex_summary_folder>"
    echo " "
    echo "      Required:"
    echo "      -p|--path               Path to data (i.e., parent of HCP) "
    echo "      -n|--name               Study Name "
    echo "      -i|--id                 Subject ID "
    echo "      -v|--visit              Visit (aka session) "
    echo "      -e|--ex-folder          Executive Summary Folder "
    echo "                                example: summary_DCANBOLDProc_v4.0.0 "
    echo " "
    echo "      Optional:"
    echo "      -h|--help        Display this message"
    exit $1
}

echo "`basename $0` $options"
debug=0
# extract options and their arguments into variables.
while true ; do
    case "$1" in
        -p|--path)
            path_to_data="$2"
            shift 2
            ;;
        -n|--name)
            study_name="$2"
            shift 2
            ;;
        -i|--id)
            subject="$2"
            shift 2
            ;;
        -v|--visit)
            visit="$2"
            shift 2
            ;;
        -e|--ex_summ_folder)
            ex_summary_folder="$2"
            shift 2
            ;;
        -h|--help)
            display_help;;
        --) shift ; break ;;
        *) echo "Unexpected error parsing args!" ; display_help 1 ;;
    esac
done

# We should check that the required args are there!

# Use command line args to setup paths
ProcessedRoot="${path_to_data}/HCP/processed/"
UnprocessedRoot="${path_to_data}/HCP/sorted/"
PathToFiles="${study_name}/sub-${subject}/ses-${visit}/files/"
ProcessedFiles="${ProcessedRoot}/${PathToFiles}"
UnprocessedFiles="${UnprocessedRoot}/${PathToFiles}"

echo "COMMAND LINE ARGUMENTS"
echo path_to_data=${path_to_data}
echo study_name=${study_name}
echo subject_id=${subject}
echo visit=${visit}
echo ex_summary_folder=${ex_summary_folder}
echo "DO NOT TOUCH THESE ARGUMENTS"

### SET UP ENVIRONMENT VARIABLES ###
source `dirname $0`"/setup_env.sh"

#matlab_template=`dirname $0`"/template_FNL_preproc_Matlab.m"

############ HELPER FUNCTIONS ##############

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
        ${wb_command} -show-scene ${temp_scene} ${scenenum} ${out} 900 800 > /dev/null 2>&1

    }

    create_image_from_template_169() {

 		total_frames=169
		for ((i=1 ; i<=${total_frames} ;  i++)); do
            if [ "$1" -eq 1 ] ; then
                scene_file=${ProcessedFiles}/t1_169_scene.scene
                out=${ex_sum_Dir}/T1_pngs/P_T1_frame_${i}.png
            elif [ "$1" -eq 2 ]; then
                scene_file=${ProcessedFiles}/t2_169_scene.scene
			    out=${ex_sum_Dir}/T2_pngs/P_T2_frame_${i}.png
            fi  			
            echo $i
   			echo ${wb_command} -show-scene ${scene_file} ${i} ${out} 900 800 
            ${wb_command} -show-scene ${scene_file} ${i} ${out} 900 800

        done
    }


################## BEGIN #########################

echo ProcessedFiles=${ProcessedFiles}
echo UnprocessedFiles=${UnprocessedFiles}
echo 


segBrain="wmparc.2.nii.gz"
segBrainDir="${ProcessedFiles}/MNINonLinear/ROIs"
wm_mask_L="L_wm_2mm_${subject}_mask.nii.gz"
wm_mask_R="R_wm_2mm_${subject}_mask.nii.gz"
wm_mask="wm_2mm_${subject}_mask.nii.gz"
wm_mask_eroded="wm_2mm_${subject}_mask_erode.nii.gz"
vent_mask_L="L_vent_2mm_${subject}_mask.nii.gz"
vent_mask_R="R_vent_2mm_${subject}_mask.nii.gz"
vent_mask="vent_2mm_${subject}_mask.nii.gz"
vent_mask_eroded="vent_2mm_${subject}_mask_eroded.nii.gz"

echo "START: executive summary"

# The summary folder must alread exist, since DCANBOLDProc must already have been run.
ex_sum_Dir="${ProcessedFiles}/${ex_summary_folder}"
echo Path to summary : ${ex_sum_Dir}

atlas=`dirname $0`"/templates/MNI152_T1_1mm_brain.nii.gz"
t1="${ProcessedFiles}/MNINonLinear/T1w_restore_brain.nii.gz"
slices ${t1} ${atlas} -o "${ex_sum_Dir}/${subject}_atlas_in_t1.gif"
slices ${atlas} ${t1} -o "${ex_sum_Dir}/${subject}_t1_in_atlas.gif"

t1="${ProcessedFiles}/MNINonLinear/T1w_restore.nii.gz"
t2="${ProcessedFiles}/MNINonLinear/T2w_restore.nii.gz"
rw="${ProcessedFiles}/MNINonLinear/fsaverage_LR32k/${subject}.R.white.32k_fs_LR.surf.gii"
rp="${ProcessedFiles}/MNINonLinear/fsaverage_LR32k/${subject}.R.pial.32k_fs_LR.surf.gii"
lw="${ProcessedFiles}/MNINonLinear/fsaverage_LR32k/${subject}.L.white.32k_fs_LR.surf.gii"
lp="${ProcessedFiles}/MNINonLinear/fsaverage_LR32k/${subject}.L.pial.32k_fs_LR.surf.gii"
t1_brain="${ProcessedFiles}/MNINonLinear/T1w_restore_brain.nii.gz"
t1_2_brain="${ProcessedFiles}/MNINonLinear/T1w_restore_brain.2.nii.gz"
has_t2=1
if [[ ! -e ${t2} ]] ; then
    echo "t2 not found"
    has_t2=0
    t2="${ProcessedFiles}/MNINonLinear/T1w_restore.nii.gz"
fi

#make t1 2mm isovoxel brain
echo flirt uses ${FSL_DIR}/data/standard/MNI152_T1_2mm_brain KJS...
flirt -in ${t1_brain} -ref ${FSL_DIR}/data/standard/MNI152_T1_2mm_brain -applyisoxfm 2 -out ${t1_2_brain}
if [[ -e ${t1_2_brain} ]] ; then
   echo success: result of flirt is in ${t1_2_brain} ...KJS.
else
   echo bummer: ${t1_2_brain} does not exist ...KJS.
fi

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
        create_image_from_template "${ex_sum_Dir}/${image_names[$i]}.png" $scenenum
    fi
done

rm -rf ${ProcessedFiles}/image_template_temp.scene

# Cannot do either 1 or 2 if there is no template
if [[ ! -e `dirname $0`/templates/parasagittal_Tx_169_template.scene ]] ; then
    echo Missing `dirname $0`/templates/parasagittal_Tx_169_template.scene KJS...
    echo Skip 169 processing ...KJS.
#create brain sprite images
elif [[ ${has_t2} -eq 1 ]] ; then
	mkdir ${ex_sum_Dir}/T1_pngs/
	mkdir ${ex_sum_Dir}/T2_pngs/
    build_txw_scene_from_template_169 $t1 $rp $lp $rw $lw 1
    create_image_from_template_169 1
    build_txw_scene_from_template_169 $t2 $rp $lp $rw $lw 2
    create_image_from_template_169 2
else
	mkdir ${ex_sum_Dir}/T1_pngs/
	build_txw_scene_from_template_169 $t1 $rp $lp $rw $lw 1
    create_image_from_template_169 1
fi

#make figures
for TASK in `ls -d ${ProcessedFiles}/*task-*` ; do
    fMRIName=`basename ${TASK}`
    rest_img="${ProcessedFiles}/MNINonLinear/Results/${fMRIName}/${fMRIName}.nii.gz"
    slices ${t1_2_brain} ${rest_img} -s 2 -o "${ex_sum_Dir}/${subject}_${fMRIName}_in_t1.gif"
    slices ${rest_img} ${t1_2_brain} -s 2 -o "${ex_sum_Dir}/${subject}_t1_in_${fMRIName}.gif"
done
echo "DONE: executive summary prep"

