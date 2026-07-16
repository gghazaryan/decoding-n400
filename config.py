"""
===========
Config file
===========
Configuration parameters for the study.
"""

import os
from socket import getfqdn
from fnames import FileNames

###############################################################################
# Determine which user is running the scripts on which machine and set the path
# where the data is stored and how many CPU cores to use. This is probably the
# only section you need to modify to replicate the pipeline as presented in van
# Vliet et al. 2018.

user = os.environ['USER']  # Username of the user running the scripts
host = getfqdn()  # Hostname of the machine running the scripts

if False:
    continue
else:
    raise RuntimeError('Please edit scripts/config.py and set the study_path and freesurfer_dir'
                       'variables to point to the location where the data '
                       'should be stored and the n_jobs variable to the '
                       'number of CPU cores the analysis is allowed to use.')



###############################################################################
# These are all the relevant parameters for the analysis. You can experiment
# with changing these.


# Time window (relative to stimulus onset) to use for extracting epochs

epoch_tmin, epoch_tmax = -0.1, 1.2

# Time window to use for computing the baseline of the epoch
baseline = (-0.1, 0)

# Thresholds to use for rejecting epochs that have a too large signal amplitude
reject = dict(grad=3E-10)

filter_list = [(0.1,40)]
highpass, lowpass = 0.1, 40
subjects = list(range(1, 27))

data_dir = study_path+"/bids"
deriv_dir = study_path+"/bids/derivatives"

###############################################################################
# Templates for filenames
#
# This part of the config file uses the FileNames class. It provides a small
# wrapper around string.format() to keep track of a list of filenames.
# See fnames.py for details on how this class works.
fname = FileNames()

fname.add('study_path', data_dir)
fname.add('deriv_path', deriv_dir)
fname.add('project_path', project_path)
fname.add('archive_path', archive_path)

fname.add('all_trials_file', '{project_path}/stimuli/target_cats.csv')
fname.add('stimuli_info', '{project_path}/stimuli/stimuli.csv')
fname.add('event_id_file', '{project_path}/stimuli/trigger_id_lookup.csv')
fname.add('block_file','/{project_path}/presentation/main/block{run}_final.txt')



# raw files and main paths


fname.add('fine_cal', "{archive_path}/calibration_files/sss_cal_Aalto_TRIUXneo_3158.dat")
fname.add('crosstalk', "{archive_path}/calibration_files/ct_sparse_Aalto_TRIUXneo_3158.fif")

fname.add('bids_base', 'sub-{subject:02d}_task-main_run-{run:02d}')

fname.add('meg_dir', '{study_path}/derivatives/meg-derivatives')
fname.add('subject_dir', '{meg_dir}/sub-{subject:02d}')
#fname.add('bad_channels', '{manual_path}/bad_channels.csv')
#fname.add('coil_order', '{manual_path}/coil_order.csv')
#fname.add('components', '{manual_path}/ica_components.csv')

# raw 

fname.add('raw', '{study_path}/sub-{subject:02d}/meg/sub-{subject:02d}_task-main_run-{run:02d}_meg.fif')
fname.add('bad_channels', '/{meg_dir}/sub-{subject:02d}/sub-{subject:02d}_bad_channels.txt')

# preprocessing

# tSSS
fname.add('tsss', '{meg_dir}/sub-{subject:02d}//{bids_base}_tsss_meg.fif')
fname.add('tsss_log', '{meg_dir}/sub-{subject:02d}/{bids_base}_tsss_meg_log.txt')

# annotate files
fname.add('annotations', '{meg_dir}/sub-{subject:02d}//{bids_base}_badsegments.csv')


# filtered data
fname.add('filtered', '{meg_dir}/sub-{subject:02d}/highpass-{highpass}_lowpass-{lowpass}/{bids_base}_tsss_filtered.fif')



# ica

fname.add('ica', '{meg_dir}/sub-{subject:02d}//{bids_base}-ica.fif')
fname.add('components', '{meg_dir}/sub-{subject:02d}/sub-{subject:02d}_bad_ica_components.txt')
fname.add('clean', '{meg_dir}/sub-{subject:02d}/highpass-{highpass}_lowpass-{lowpass}/{bids_base}_tsss_filtered_clean.fif')



fname.add('dirty_epo', '{meg_dir}/sub-{subject:02d}/{bids_base}_dirty-epo.fif')
fname.add('eog_epo', '{meg_dir}/sub-{subject:02d}/{bids_base}_eog-epo.fif')
fname.add('ecg_epo', '{meg_dir}/sub-{subject:02d}/{bids_base}_ecg-epo.fif')

#epochs
fname.add('clean_epo_run', '{meg_dir}/sub-{subject:02d}/highpass-{highpass}_lowpass-{lowpass}/{bids_base}_clean-epo.fif')
fname.add('clean_epo_run_long', '{meg_dir}/sub-{subject:02d}/highpass-{highpass}_lowpass-{lowpass}/{bids_base}_long_clean-epo.fif')
fname.add('clean_epo_merged', '{meg_dir}/sub-{subject:02d}/highpass-{highpass}_lowpass-{lowpass}/sub-{subject:02d}_{position}_clean-epo.fif')
fname.add('clean_epo_merged_long', '{meg_dir}/sub-{subject:02d}/highpass-{highpass}_lowpass-{lowpass}/sub-{subject:02d}_{position}_long_clean-epo.fif')

fname.add('clean_epo_merged_dropbad', '{meg_dir}/sub-{subject:02d}/highpass-{highpass}_lowpass-{lowpass}/sub-{subject:02d}_{position}_dropbad_clean-epo.fif')
fname.add('dropbad_list', '{meg_dir}/sub-{subject:02d}/highpass-{highpass}_lowpass-{lowpass}/sub-{subject:02d}_{position}_dropbad_list.txt')




fname.add('ave_positions', '{subject_dir}/highpass-{highpass}_lowpass-{lowpass}/evokeds/sub-{subject:02d}_position-ave.fif')
fname.add('ave_levels', '{subject_dir}/highpass-{highpass}_lowpass-{lowpass}/evokeds/sub-{subject:02d}_levels-{position}-ave.fif')
fname.add('ave_indiv', '{subject_dir}/highpass-{highpass}_lowpass-{lowpass}/evokeds/sub-{subject:02d}_level-{level}-{position}-items-ave.fif')
fname.add('ave_indiv_single', '{subject_dir}/highpass-{highpass}_lowpass-{lowpass}/evokeds/sub-{subject:02d}_level-{level}-{position}-items-single_trials-ave.fif')


fname.add('ave_indiv_head_same', '{subject_dir}/highpass-{highpass}_lowpass-{lowpass}/evokeds/head_same/sub-{subject:02d}_head_same_level-{level}-{position}-items-ave.fif')
fname.add('ave_indiv_head_same_single', '{subject_dir}/highpass-{highpass}_lowpass-{lowpass}/evokeds/head_same/sub-{subject:02d}_head_same_level-{level}-{position}-items-single_trials-ave.fif')


fname.add('trans_log', '{subject_dir}/highpass-{highpass}_lowpass-{lowpass}/evokeds/head_same/sub-{subject:02d}_level-{level}-{position}_trans_log.txt')
fname.add('trans_log_single', '{subject_dir}/highpass-{highpass}_lowpass-{lowpass}/evokeds/head_same/sub-{subject:02d}_level-{level}-{position}_trans_log_single.txt')

fname.add('grand_average_items', '{meg_dir}/average/highpass-{highpass}_lowpass-{lowpass}/evokeds/average_level-{level}-{position}_items.fif')
fname.add('grand_average_small_cat', '{meg_dir}/average/highpass-{highpass}_lowpass-{lowpass}/evokeds/average_level-{level}-{position}_small_cat.fif')
fname.add('grand_average_big_cat', '{meg_dir}/average/highpass-{highpass}_lowpass-{lowpass}/evokeds/average_level-{level}-{position}_big_cat.fif')

fname.add('grand_average_items_single', '{meg_dir}/average/highpass-{highpass}_lowpass-{lowpass}/evokeds/average_level-{level}-{position}_single_trials-items.fif')



fname.add('ave_long', '{subject_dir}/highpass-{highpass}_lowpass-{lowpass}/evokeds/sub-{subject:02d}_long-ave.fif')
fname.add('ave_long_levels', '{subject_dir}/highpass-{highpass}_lowpass-{lowpass}/evokeds/sub-{subject:02d}_long_levels-ave.fif')
fname.add('ave_long_indiv', '{subject_dir}/highpass-{highpass}_lowpass-{lowpass}/evokeds/sub-{subject:02d}_long_level-{level}-{position}-items-ave.fif')



fname.add('evoked', '{meg_dir}/sub-{subject:02d}/sub-{subject:02d}_{position}-{level}-ave.fif')
fname.add('evoked_long', '{meg_dir}/sub-{subject:02d}/sub-{subject:02d}_prime1-{level}-long-ave.fif')


fname.add('clean_epo_merged_long_baseold', '{meg_dir}/sub-{subject:02d}/sub-{subject:02d}_{position}_long_base_old_clean-epo.fif')

fname.add('clean_epo_merged_average', '{meg_dir}/average/average_{position}_clean-epo.fif')
fname.add('evoked_average', '{meg_dir}/average/average_{position}-{level}_ave.fif')


# test files
fname.add('clean_epo_split', '{meg_dir}/sub-{subject:02d}/sub-{subject:02d}_{position}_clean-epo.fif')
fname.add('all_clean_epo_test', '{meg_dir}/sub-{subject:02d}/sub-{subject:02d}_highpass-{highpass}_lowpass-{lowpass}_all_clean-epo.fif')
fname.add('clean_epo_split_test', '{meg_dir}/sub-{subject:02d}/sub-{subject:02d}_highpass-{highpass}_lowpass-{lowpass}_{position}_clean-epo.fif')


# matrices
fname.add('mat', '{subject_dir}/highpass-{highpass}_lowpass-{lowpass}/matrices/sub-{subject:02d}_position-{position}_level-{level}.mat')
fname.add('mat_concat_cv', '{subject_dir}/highpass-{highpass}_lowpass-{lowpass}/matrices/sub-{subject:02d}_position-{position}_level-{level}_train_cv.mat')


fname.add('mat_average', '{meg_dir}/average/highpass-{highpass}_lowpass-{lowpass}/matrices/average_position-{position}_level-{level}_channels-{ch_type}.mat')

# Filenames for MNE reports
fname.add('reports_dir', '{study_path}/derivatives/reports/sub-{subject:02d}/{analysis}/')
fname.add('report', '{reports_dir}/sub-{subject:02d}-{step}_report.h5')
fname.add('report_html', '{reports_dir}/sub-{subject:02d}-{step}-report.html')
fname.add('report_html_average', '{study_path}/derivatives/reports/average/{analysis}//average-{step}-report.html')
fname.add('report_path','{study_path}/reports/sub-{subject:02d}/preprocessing/evokeds/')

# Freesurfer dir


fname.add('freesurfer_dir', f"{freesurfer_dir}")
fname.add('freesurfer_subjects_dir', '{freesurfer_dir}/freesurfer_subjects')
fname.add('trans_coreg','{freesurfer_subjects_dir}/sub-{subject:02d}/bem/sub-{subject:02d}-coreg_trans.fif')
fname.add('bem','{freesurfer_subjects_dir}/sub-{subject:02d}/bem/sub-{subject:02d}-ico4-bem-sol.fif')
fname.add('src','{freesurfer_subjects_dir}/sub-{subject:02d}/bem/sub-{subject:02d}-ico-4-src.fif')
fname.add('noise_cov','{freesurfer_subjects_dir}/sub-{subject:02d}/bem/sub-{subject:02d}-noise-cov.fif')
fname.add('inv','{freesurfer_subjects_dir}/sub-{subject:02d}/bem/sub-{subject:02d}-inv.fif')
fname.add('fwd','{freesurfer_subjects_dir}/sub-{subject:02d}/bem/sub-{subject:02d}-ico4-fwd-sol.fif')



# source localized data and rsa
fname.add('all_items_stc','{deriv_path}/source-level/sub-{subject:02d}/stcs/sub-{subject:02d}-{level}-items_all')
fname.add('all_items_stc_morphed','{deriv_path}/source-level/sub-{subject:02d}/stcs/sub-{subject:02d}-{level}-items_all_morphed')

fname.add('indiv_item_stc','{deriv_path}/source-level/sub-{subject:02d}/stcs/indiv/{level}/sub-{subject:02d}-{level}-{item}')
fname.add('indiv_item_stc_morphed','{deriv_path}/source-level/sub-{subject:02d}/stcs/indiv/{level}/sub-{subject:02d}-{level}_{item}-morphed')

fname.add('src_fsaverage','{freesurfer_subjects_dir}/fsaverage_source/fsaverage-ico4-src.fif')
fname.add('average_stc','{deriv_path}/source-level/group_average/average-{level}-all_items')
fname.add('item_average_stc','{deriv_path}/source-level/group_average/items/average-{level}-{item}')

fname.add('rsa','{deriv_path}/source-level/sub-{subject:02d}/rsa/{level}/t-{window_size}/sub-{subject:02d}_spatial-{spatial_radius}_dsm-{dsm_metric}_rsa-{rsa_metric}_{level}')
fname.add('rsa_morphed','{deriv_path}/source-level/sub-{subject:02d}/rsa/{level}/t-{window_size}/sub-{subject:02d}_spatial-{spatial_radius}_dsm-{dsm_metric}_rsa-{rsa_metric}_{level}_morphed')

fname.add('rsa_subject_average','{deriv_path}/source-level/group_average/rsa/{level}/t-{window_size}/subject_average_spatial-{spatial_radius}_dsm-{dsm_metric}_rsa-{rsa_metric}_{level}')

fname.add('rsa_average','{deriv_path}/source-level/group_average/rsa/{level}/t-{window_size}/average_spatial-{spatial_radius}_dsm-{dsm_metric}_rsa-{rsa_metric}_{level}')

#source=level mats

fname.add('average_stc_mat','{deriv_path}/source-level/group_average/decoding_mats/average-{level}_{tmin}-{tmax}.mat')
fname.add('indiv_stc_mat','{deriv_path}/source-level/sub-{subject:02d}/decoding_mats/sub-{subject:02d}-{level}.mat')


#fname.add('bem_fsaverage','{freesurfer_subjects_dir}/fsaverage_source/fsaverage-ico4-bem-sol.fif')




fname.add('all_items_stc_long','{freesurfer_subjects_dir}/sub-{subject:02d}/source/stcs/sub-{subject:02d}-{level}-all_long_stc')


os.environ["SUBJECTS_DIR"] = fname.freesurfer_subjects_dir
