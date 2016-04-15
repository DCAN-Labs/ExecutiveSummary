#!/bin/bash
# shannon t. buckley
review_folder=/group_shares/FAIR_LAB2/Projects/FAIR_users/Shannon/QC_todo/
date_stamp=$(date | awk '{print $1 $2 $3}')
mkdir ${review_folder}/${date_stamp}
case_folder=${review_folder}${date_stamp}
cp T{1,2}-*.png $case_folder
cp *.gif $case_folder
cp -R ./img $case_folder
cp DVARS_and_FD_CONCA.png $case_folder
cp executive_summary*.html $case_folder
