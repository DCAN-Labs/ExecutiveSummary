#!/bin/bash

# Note: This file was copied from FNL_preproc_preproc.sh.
# It performs the steps needed to prep for exec summary. It does NOT call FNL_preproc.sh.

options=`getopt -o i:o:d:s:v:a:b:p:hx -l bids-input:,output-dir:,html-path:,subject-id:,session-id:,atlas:,brainsprite-template:,pngs-template:,help,skip_sprite -n 'executivesummary_preproc.sh' -- $@`
eval set -- "$options"
function display_help() {
    echo "Usage: `basename $0` [options...]                                                                             "
    echo "                                                                                                              "
    echo "      Required:                                                                                               "
    echo "      -o|--output-dir           Path to processed files, ending at files.                                     "
    echo "      -s|--subject-id           Subject ID without sub- prefix.                                               "
    echo "                                                                                                              "
    echo "      Optional:                                                                                               "
    echo "      -w|--html-path            Path to which to write executive summary. Default is                          "
    echo "                                <output-dir>/executivesummary.                                                "
    echo "      -i|--bids-input           Path to unprocessed data set, ending at func. If not supplied, no task data   "
    echo "                                will be processed.                                                            "
    echo "      -v|--session-id           Session (visit) ID without ses- prefix.                                       "
    echo "      -a|--atlas                Atlas file for generation of rest image. Overrides adult MNI 1mm atlas.       "
    echo "      -b|--brainsprite-template Path to template that has all of the scenes for the brainsprite (usually 169)."
    echo "      -p|--pngs-template        Path to template with scenes for Tx pngs (these are named, so should agree).  "
    echo "      -h|--help                 Display this message.                                                         "
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
        -s|--subject-id)
            subject_id="$2"
            shift 2
            ;;
        -w|--html-path)
            html_path="$2"
            shift 2
            ;;
        -v|--session-id)
            session_id="$2"
            shift 2
            ;;
        -a|--atlas)
            atlas="$2"
            shift 2
            ;;
        -b|--brainsprite-template)
            brainsprite_template="$2"
            shift 2
            ;;
        -p|--pngs-template)
            pngs_template="$2"
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

# Check for required args.
if [ -z "${output_dir}" ] || [ -z "${subject_id}" ] ; then
    echo output-dir and subject-id are required.
    display_help
fi

# Log the args.
echo
echo COMMAND LINE ARGUMENTS to $0:
echo output-dir=${output_dir}
echo subject-id=${subject_id}
echo html-path=${html_path}
echo bids-input=${bids_input}
echo session-id=${session_id}
echo atlas=${atlas}

if [ -n "${skip_sprite}" ] ; then
    # This is a 'stealth' arg.
    echo Skip sprite processing.
fi

echo End of args.


### SET UP ENVIRONMENT VARIABLES ###
scriptdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source ${scriptdir}/setup_env.sh
templatedir=${scriptdir}/templates
if [ -z "${GROUP}" ] ; then
    GROUP=fnl_lab
fi

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

AtlasSpacePath=${processed_files}/${AtlasSpaceFolder}
Results=${AtlasSpacePath}/Results
ROIs=${AtlasSpacePath}/ROIs

if [ -z "${atlas}" ] ; then
    echo Use default atlas.
    atlas=${templatedir}/MNI152_T1_1mm_brain.nii.gz # Note: there is one of these in $FSLDIR/data/standard, but if differs. Why?
else
    echo Use atlas: $atlas
fi
echo


if [ -z "${html_path}" ] || [[ "NONE" == "${html_path}" ]] ; then
    # The summary directory was not supplied, write to the output-dir ('files').
    html_path=${processed_files}/executivesummary
fi
if ! [ -d ${html_path} ]; then
    # The summary directory was supplied, but does not yet exist.
    mkdir -p ${html_path}
    chown :${GROUP} ${html_path} || true
    chmod 770 ${html_path} || true
fi

# Make the subfolder for the images. All paths in the html are relative to
# the html folder, so must img must remain a subfolder to the html folder.

# Lose old images.
images_path=${exsum_path}/img
if [ -d ${images_path} ] ; then
    echo Remove images from prior runs.
    if [ -n "${skip_sprite}" ] ; then
        # Cheat - keep the mosaics, and don't bother to log each file removed.
        # (For debug only.)
        mv ${images_path}/*mosaic* ${exsum_path}
        rm -f ${images_path}/*
        mv ${exsum_path}/*mosaic* .
    else
        for FILE in $( ls ${images_path}/* ) ; do
            echo rm -f ${FILE}
            rm -f ${FILE}
        done
    fi
fi
mkdir -p ${images_path}
if ! [ -d ${images_path} ] ; then
    echo Unable to write ${images_path}. Permissions?
    echo Exiting.
    exit 1
fi

# Sometimes need a "working directory"
working=${exsum_path}/temp_files
mkdir -p ${working}
if ! [ -d ${working} ] ; then
    echo Unable to write ${working}. Permissions?
    echo Exiting.
    exit 1
fi

chown -R :${GROUP} ${exsum_path} || true
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
    build_scene_from_pngs_template(){
        # Make a copy of the scene template as we will be making modifications.
        cp ${pngs_template} ${pngs_scene}

        declare -a templates=('T2_IMG' 'T1_IMG' 'RPIAL' 'LPIAL' 'RWHITE' 'LWHITE')
        declare -a paths=($1 $2 $3 $4 $5 $6)

        for i in `seq 0 5`;
        do
            # Replace templated pathnames and filenames in local copy.
            sed -i "s!${templates[$i]}_PATH!${paths[$i]}!g" ${pngs_scene}
            filename=$(basename "${paths[$i]}")
            sed -i "s!${templates[$i]}_NAME!${filename}!g" ${pngs_scene}
        done
    }

    build_scene_from_brainsprite_template(){
        # Make a copy of the brainsprite_scene template as we will be making modifications.
        cp ${brainsprite_template} ${brainsprite_scene}

        declare -a templates=('TX_IMG' 'R_PIAL' 'L_PIAL' 'R_WHITE' 'L_WHITE')
        declare -a paths=($1 $2 $3 $4 $5)

        for i in `seq 0 4`; do
            # Replace templated pathnames and filenames in local copy.
            echo sed -i "s!${templates[$i]}_NAME_and_PATH!${paths[$i]}!g" ${brainsprite_scene}
            sed -i "s!${templates[$i]}_NAME_and_PATH!${paths[$i]}!g" ${brainsprite_scene}
            filename=$(basename "${paths[$i]}")
            echo sed -i "s!${templates[$i]}_NAME!${filename}!g" ${brainsprite_scene}
            sed -i "s!${templates[$i]}_NAME!${filename}!g" ${brainsprite_scene}
        done
    }

    #takes the following arguments: out_path scenenum
    create_image_from_pngs_scene() {
        out=$1
        scenenum=$2
        ${wb_command} -show-scene ${pngs_scene} ${scenenum} ${out} 900 800

    }

    create_images_from_brainsprite_scene() {
        Tx=${1}
        total_frames=$( grep "SceneInfo Index=" ${brainsprite_scene} | wc -l )

        for ((i=1 ; i<=${total_frames} ;  i++)); do
            out=${processed_files}/${Tx}_pngs/P_${Tx}_frame_${i}.png
            echo $i
            echo ${wb_command} -show-scene ${brainsprite_scene} ${i} ${out} 900 800
            ${wb_command} -show-scene ${brainsprite_scene} ${i} ${out} 900 800
        done
    }


    make_default_slices_row() {
        # This function uses the default slices made by slicesdir (.4, .5, and
        # .6). It calls slicesdir, grabs the output png, and cleans up the
        # subdirectory left by slicesdir (also called slicesdir).
        # Note: everything must be "local" or we get horrible filenames. Also,
        # this whole process makes a mess. So use the working directory.

        base_img=$1
        out_png=$2
        red_img=$3 # optional

        img_file=$( basename ${base_img} )
        img_png=${img_file/.nii.gz/.png}

        pushd ${working}
        imcp ${base_img} ./${img_file}

        if [ -n "${red_img}" ] ; then
            red_file=$( basename ${red_img} )
            imcp ${red_img} ./${red_file}
            slicesdir -p ${red_file} ${img_file}
        else
            slicesdir ${img_file}
        fi
        mv slicesdir/${img_png} ${out_png}

        rm -rf slicesdir
        popd
    }

################## BEGIN #########################

wm_mask_L="L_wm_2mm_${subject_id}_mask.nii.gz"
wm_mask_R="R_wm_2mm_${subject_id}_mask.nii.gz"
wm_mask="wm_2mm_${subject_id}_mask.nii.gz"
wm_mask_eroded="wm_2mm_${subject_id}_mask_erode.nii.gz"
vent_mask_L="L_vent_2mm_${subject_id}_mask.nii.gz"
vent_mask_R="R_vent_2mm_${subject_id}_mask.nii.gz"
vent_mask="vent_2mm_${subject_id}_mask.nii.gz"
vent_mask_eroded="vent_2mm_${subject_id}_mask_eroded.nii.gz"

echo
echo "START: executive summary image preprocessing"

set -e

############
### Anat
############
images_pre=${images_path}/sub-${subject_id}
if [ -n "${session_id}" ] ; then
    images_pre=${images_pre}_ses-${session_id}
fi
t1_mask=${AtlasSpacePath}/T1w_restore_brain.nii.gz

if [ -z "${atlas}" ] ; then
    echo The atlas argument was not supplied. Cannot create atlas-in-t1 or t1-in-atlas
elif [[ ! -e ${atlas} ]] ; then
    echo "Missing ${atlas}"
    echo "Cannot create atlas-in-t1 or t1-in-atlas"
else
    echo Registering $( basename ${t1_mask} ) and atlas file: ${atlas}
    set -x
    make_default_slices_row ${t1_mask} ${images_pre}_desc-AtlasInT1w.gif ${atlas}
    make_default_slices_row ${atlas} ${images_pre}_desc-T1wInAtlas.gif ${t1_mask}
    set +x
fi

# From here on, use the whole T1 file rather than the mask (used above).
t1="${AtlasSpacePath}/T1w_restore.nii.gz"
t2="${AtlasSpacePath}/T2w_restore.nii.gz"
has_t2=1
if [[ ! -e ${t2} ]] ; then
    echo "t2 not found; using t1"
    has_t2=0
    t2="${t1}"
fi

rw="${AtlasSpacePath}/fsaverage_LR32k/${subject_id}.R.white.32k_fs_LR.surf.gii"
rp="${AtlasSpacePath}/fsaverage_LR32k/${subject_id}.R.pial.32k_fs_LR.surf.gii"
lw="${AtlasSpacePath}/fsaverage_LR32k/${subject_id}.L.white.32k_fs_LR.surf.gii"
lp="${AtlasSpacePath}/fsaverage_LR32k/${subject_id}.L.pial.32k_fs_LR.surf.gii"
t1_brain="${AtlasSpacePath}/T1w_restore_brain.nii.gz"
t2_brain="${AtlasSpacePath}/T2w_restore_brain.nii.gz"

# Make named pngs to show specific anatomical areas.
if [ -z "${pngs_template}" ]; then
    # Use default.
    pngs_template=${templatedir}/image_template_temp.scene
fi

pngs_scene=${processed_files}/pngs_scene.scene
build_scene_from_pngs_template $t2 $t1 $rp $lp $rw $lw
declare -a image_names=('T1-Axial-InferiorTemporal-Cerebellum' 'T2-Axial-InferiorTemporal-Cerebellum' 'T1-Axial-BasalGangila-Putamen' 'T2-Axial-BasalGangila-Putamen' 'T1-Axial-SuperiorFrontal' 'T2-Axial-SuperiorFrontal' 'T1-Coronal-PosteriorParietal-Lingual' 'T2-Coronal-PosteriorParietal-Lingual' 'T1-Coronal-Caudate-Amygdala' 'T2-Coronal-Caudate-Amygdala' 'T1-Coronal-OrbitoFrontal' 'T2-Coronal-OrbitoFrontal' 'T1-Sagittal-Insula-FrontoTemporal' 'T2-Sagittal-Insula-FrontoTemporal' 'T1-Sagittal-CorpusCallosum' 'T2-Sagittal-CorpusCallosum' 'T1-Sagittal-Insula-Temporal-HippocampalSulcus' 'T2-Sagittal-Insula-Temporal-HippocampalSulcus')
((num_wb_scenes=${#image_names[@]}-1))

for i in `seq 0 ${num_wb_scenes}`;
do
    ((scenenum=(i+1)))

    if [[ ${has_t2} -eq 0 && $(( $scenenum % 2 )) -eq 0 ]] ; then
        echo "skip t2 image"
    else
        echo create_image_from_pngs_scene "${images_pre}_${image_names[$i]}.png" $scenenum
        create_image_from_pngs_scene "${images_pre}_${image_names[$i]}.png" $scenenum
    fi
done

rm -rf ${pngs_scene}


# Make pngs to be used for the brainsprite.
if [ -z "${brainsprite_template}" ]; then
    # Use default.
    brainsprite_template=${templatedir}/parasagittal_Tx_169_template.scene
fi
if [ -n "${skip_sprite}" ] ; then
    # Skip brainsprite processing.
    echo Skip brainsprite processing per user request.
elif [[ ! -e ${brainsprite_template} ]] ; then
    # Cannot do brainsprite processing if there is no template
    echo Missing ${brainsprite_template}
    echo Cannot perform processing needed for brainsprite.
else
    mkdir -p ${processed_files}/T1_pngs/
    chown :${GROUP} ${processed_files}/T1_pngs/ || true
    chmod 770 ${processed_files}/T1_pngs/ || true

    # Create brainsprite images for T1
    brainsprite_scene=${processed_files}/t1_bs_scene.scene
    build_scene_from_brainsprite_template $t1 $rp $lp $rw $lw
    create_images_from_brainsprite_scene T1

    if [[ ${has_t2} -eq 1 ]] ; then
        mkdir -p ${processed_files}/T2_pngs/
        chown :${GROUP} ${processed_files}/T2_pngs/ || true
        chmod 770 ${processed_files}/T2_pngs/ || true

        # Create brainsprite images for T2
        brainsprite_scene=${processed_files}/t2_bs_scene.scene
        build_scene_from_brainsprite_template $t2 $rp $lp $rw $lw
        create_images_from_brainsprite_scene T2
    fi
fi

# Subcorticals
subcort_sub=${ROIs}/sub2atl_ROI.2.nii.gz
subcort_atl=${ROIs}/Atlas_ROIs.2.nii.gz
set -x
if [ -e ${subcort_sub} ] ; then
    if [ -e ${subcort_atl} ] ; then
        echo Create subcorticals images.

        # The default slices are not as nice for subcorticals as they are for
        # a whole brain. Pick out slices using slicer.

        pushd ${working}
        imcp ${subcort_sub} ./subcort_sub.nii.gz
        imcp ${subcort_atl} ./subcort_atl.nii.gz

        prefix="slice_"

        # slices/slicer does not do well trying to make the red outline when it
        # cannot find the edges, so cannot use the ROI files with some low
        # intensities.
        # Make a binarized copy of the subcortical atlas to be used for the
        # outline.
        bin_atl=bin_subcort_atl.nii.gz
        fslmaths subcort_atl.nii.gz -bin ${bin_atl}

        # Sagittal slices:
        slicer subcort_sub.nii.gz ${bin_atl} -x -36 ${prefix}a.png -u -L
        slicer subcort_sub.nii.gz ${bin_atl} -x -45 ${prefix}b.png -u -L
        slicer subcort_sub.nii.gz ${bin_atl} -x -52 ${prefix}c.png -u -L
        # Coronal slices:
        slicer subcort_sub.nii.gz ${bin_atl} -y -43 ${prefix}d.png -u -L
        slicer subcort_sub.nii.gz ${bin_atl} -y -54 ${prefix}e.png -u -L
        slicer subcort_sub.nii.gz ${bin_atl} -y -65 ${prefix}f.png -u -L
        # Axial slices:
        slicer subcort_sub.nii.gz ${bin_atl} -z -23 ${prefix}g.png -u -L
        slicer subcort_sub.nii.gz ${bin_atl} -z -33 ${prefix}h.png -u -L
        slicer subcort_sub.nii.gz ${bin_atl} -z -39 ${prefix}i.png -u -L

        pngappend ${prefix}a.png + ${prefix}b.png + ${prefix}c.png + \
                   ${prefix}d.png + ${prefix}e.png + ${prefix}f.png + \
                   ${prefix}g.png + ${prefix}h.png + ${prefix}i.png \
                   ${images_pre}_desc-AtlasInSubcort.gif

        # Make a binarized copy of the subject's subcorticals to be used
        # for the outline.
        bin_sub=bin_subcort_sub.nii.gz
        fslmaths subcort_sub.nii.gz -bin ${bin_sub}

        # Sagittal slices:
        slicer subcort_atl.nii.gz ${bin_sub} -x -36 ${prefix}a.png -u -L
        slicer subcort_atl.nii.gz ${bin_sub} -x -45 ${prefix}b.png -u -L
        slicer subcort_atl.nii.gz ${bin_sub} -x -52 ${prefix}c.png -u -L
        # Coronal slices:
        slicer subcort_atl.nii.gz ${bin_sub} -y -43 ${prefix}d.png -u -L
        slicer subcort_atl.nii.gz ${bin_sub} -y -54 ${prefix}e.png -u -L
        slicer subcort_atl.nii.gz ${bin_sub} -y -65 ${prefix}f.png -u -L
        # Axial slices:
        slicer subcort_atl.nii.gz ${bin_sub} -z -23 ${prefix}g.png -u -L
        slicer subcort_atl.nii.gz ${bin_sub} -z -33 ${prefix}h.png -u -L
        slicer subcort_atl.nii.gz ${bin_sub} -z -39 ${prefix}i.png -u -L

        pngappend ${prefix}a.png + ${prefix}b.png + ${prefix}c.png + \
                   ${prefix}d.png + ${prefix}e.png + ${prefix}f.png + \
                   ${prefix}g.png + ${prefix}h.png + ${prefix}i.png \
                   ${images_pre}_desc-SubcortInAtlas.gif

        popd

    else
        echo Missing ${subcort_atlas}.
        echo Cannot create atlas-in-subcort or subcort-in-atlas.
    fi
else
    echo Missing ${subcort}.
    echo No subcorticals will be included.
fi
set +x


############
### Tasks
############

t1_2_brain=${AtlasSpacePath}/T1w_restore_brain.2.nii.gz
t2_2_brain=${AtlasSpacePath}/T2w_restore_brain.2.nii.gz

if [[ -e ${t1_2_brain_img} ]] ; then
    echo "removing old resampled t1 brain"
    rm ${t1_2_brain_img}
fi
if [[ -e ${t2_2_brain_img} ]] ; then
    echo "removing old resampled t2 brain"
    rm ${t2_2_brain_img}
fi

# Make T1w and T2w task images.
for TASK in `ls -d ${processed_files}/*task-*` ; do
    fMRIName=$( basename ${TASK} )
    echo Make images for ${fMRIName}.
    task_img="${Results}/${fMRIName}/${fMRIName}.nii.gz"

    # Use the first task image to make the resampled brain.
    flirt -in ${t1_brain} -ref ${task_img} -applyxfm -out ${t1_2_brain}
    echo result of flirt is in ${t1_2_brain}
    flirt -in ${t2_brain} -ref ${task_img} -applyxfm -out ${t2_2_brain}
    echo result of flirt is in ${t2_2_brain}

    fMRI_pre=${images_path}/sub-${subject_id}_${fMRIName}
    set -x
    make_default_slices_row ${task_img} ${fMRI_pre}_desc-T1InTask.gif ${t1_2_brain}
    make_default_slices_row ${t1_2_brain} ${fMRI_pre}_desc-TaskInT1.gif ${task_img}
    make_default_slices_row ${task_img} ${fMRI_pre}_desc-T2InTask.gif ${t2_2_brain}
    make_default_slices_row ${t2_2_brain} ${fMRI_pre}_desc-TaskInT2.gif ${task_img}
    set +x
done

set -x
# If the bids-input was supplied and there are func files, slice
# the bold and sbrefs into pngs so we can display them.
shopt -s nullglob
if [ -n "${bids_input}" ] && [ -d ${bids_input} ] ; then

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
        scouts=( ${processed_files}/*task-*/Scout_orig.nii.gz ) 
        for SCOUT in ${scouts[@]} ; do
            # Get the task name and number from the parent.
            task_name=$( basename  $( dirname ${SCOUT} ) )
            png_name=sub-${subject_id}_${task_name}_ref.png
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

else
    echo No func files. Neither BOLD nor SBREF will be shown.
fi
shopt -u nullglob

set +x

# cleanup working dir
rm -rf ${working}

echo "DONE: executive summary prep"

