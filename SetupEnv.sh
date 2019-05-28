#!/bin/bash

# Set up FSL (if not already done so in the running environment)
# Uncomment the following 2 lines (remove the leading #) and correct the FSLDIR setting for your setup
export FSLDIR=/opt/installed/fsl-5.0.10
. ${FSLDIR}/etc/fslconf/fsl.sh > /dev/null 2>&1

# Let FreeSurfer know what version of FSL to use
# FreeSurfer uses FSL_DIR instead of FSLDIR to determine the FSL version
export FSL_DIR="${FSLDIR}"

# Set up FreeSurfer (if not already done so in the running environment)
# Uncomment the following 2 lines (remove the leading #) and correct the FREESURFER_HOME setting for your setup
export FREESURFER_HOME=/home/exacloud/lustre1/fnl_lab/code/external/utilities/freesurfer-5.3.0-HCP
. ${FREESURFER_HOME}/SetUpFreeSurfer.sh > /dev/null 2>&1

# Set up specific environment variables for the HCP Pipeline
export HCPPIPEDIR=/home/exacloud/lustre1/fnl_lab/code/internal/pipelines/HCP_release_20170910_v2.0
export SCRATCHDIR=/mnt/scratch

export HCPPIPEDIR_Templates=${HCPPIPEDIR}/global/templates
export HCPPIPEDIR_Config=${HCPPIPEDIR}/global/config
export HCPPIPEDIR_PreFS=${HCPPIPEDIR}/PreFreeSurfer/scripts
export HCPPIPEDIR_FS=${HCPPIPEDIR}/FreeSurfer/scripts
export HCPPIPEDIR_PostFS=${HCPPIPEDIR}/PostFreeSurfer/scripts
export HCPPIPEDIR_fMRISurf=${HCPPIPEDIR}/fMRISurface/scripts
export HCPPIPEDIR_fMRIVol=${HCPPIPEDIR}/fMRIVolume/scripts
export HCPPIPEDIR_tfMRI=${HCPPIPEDIR}/tfMRI/scripts
export HCPPIPEDIR_dMRI=${HCPPIPEDIR}/DiffusionPreprocessing/scripts
export HCPPIPEDIR_dMRITract=${HCPPIPEDIR}/DiffusionTractography/scripts
export HCPPIPEDIR_Global=${HCPPIPEDIR}/global/scripts
export HCPPIPEDIR_tfMRIAnalysis=${HCPPIPEDIR}/TaskfMRIAnalysis/scripts
export MSMCONFIGDIR=${HCPPIPEDIR}/MSMConfig
export MSMBin=${HCPPIPEDIR}/MSMBinaries


# Set up DCAN Environment Variables
export MCRROOT=/home/exacloud/lustre1/fnl_lab/code/external/utilities/MATLAB_MCR/v91
export DCANBOLDPROCDIR=/home/exacloud/lustre1/fnl_lab/code/internal/utilities/DCAN_bold_proc
export DCANBOLDPROCVER=DCANBOLDProc_v4.0.0
#export EXECSUMDIR=/home/exacloud/lustre1/fnl_lab/code/internal/utilities/executivesummary-bids
export EXECSUMDIR=/home/exacloud/tempwork/fnl_lab/sniderk/executivesummary
export ABCDTASKPREPDIR=/home/exacloud/lustre1/fnl_lab/code/internal/utilities/ABCD/ABCD_tfMRI
export SOURCEDATADIR=/home/exacloud/lustre1/fnl_lab/data/HCP/sourcedata/ABCD
export CUSTOMCLEANDIR=/home/exacloud/lustre1/fnl_lab/code/internal/utilities/custom-clean-abcd-bids-v1.0.0

# binary dependencies
export ANTSPATH=/home/exacloud/lustre1/fnl_lab/code/external/ANTs/antsbin/bin
export C3DPATH=/home/exacloud/lustre1/fnl_lab/code/external/utilities/c3d-1.1.0-Linux-x86_64/bin
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/home/exacloud/lustre1/fnl_lab/code/external/utilities/MATLAB_MCR/v91/runtime/glnxa64:/home/exacloud/lustre1/fnl_lab/code/external/utilities/MATLAB_MCR/v91/bin/glnxa64:/home/exacloud/lustre1/fnl_lab/code/external/utilities/MATLAB_MCR/v91/sys/os/glnxa64:/home/exacloud/lustre1/fnl_lab/code/external/utilities/lib64
export MSMBINDIR=/home/exacloud/lustre1/fnl_lab/code/external/utilities/MSM/homes/ecr05/MSM_HOCR_v2/Centos
export CARET7DIR=/home/exacloud/lustre1/fnl_lab/code/external/utilities/workbench-1.3.2/bin_rh_linux64
export WORKBENCHDIR=${CARET7DIR}
export OMP_NUM_THREADS=1
export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=1
export TMPDIR=/tmp
export LANG="en_US.UTF-8"
