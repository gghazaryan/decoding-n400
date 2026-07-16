#!/bin/bash 
#SBATCH --time=00:30:00
#SBATCH --mem-per-cpu=2G
#SBATCH --array=1-1000

perm=$SLURM_ARRAY_TASK_ID

train_vectors='data/word2vec_vectors_final.mat'


sub="average"

position='target'
level=$1 #train_level
#level="combined"
test_level=$1
ch_type='grad'
window=$2

python 03_decoding/zero_shot_run.py 'data/matrices/'$sub'_position-'$position'_level-'$level'_'$window'_channels-'$ch_type'.mat' \
-input_file2 'data/matrices/'$sub'_position-'$position'_level-'$test_level'_'$window'_channels-'$ch_type'.mat' \
-o 'results/decoding_windows/perm/'$level'/'$sub'_position-'$position'_train_level-'$level'_test_level-'$test_level'_channels-'$ch_type'-'$window'_window_perm-'$perm'.mat' -n $train_vectors -v  -p $perm

python 03_decoding/zero_shot_analyze_results.py 'results/decoding_windows/perm/'$level'/'$sub'_position-'$position'_train_level-'$level'_test_level-'$test_level'_channels-'$ch_type'-'$window'_window_perm-'$perm'.mat' \
-o 'results/decoding_windows/perm/'$level'/'$sub'_position-'$position'_train_level-'$level'_test_level-'$test_level'_channels-'$ch_type'-'$window'_window_perm-'$perm'.csv'
rm 'results/decoding_windows/perm/'$level'/'$sub'_position-'$position'_train_level-'$level'_test_level-'$test_level'_channels-'$ch_type'-'$window'_window_perm-'$perm'.mat' 
