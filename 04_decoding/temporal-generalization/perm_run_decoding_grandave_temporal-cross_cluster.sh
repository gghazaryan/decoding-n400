#!/bin/bash 
#SBATCH --time=04:00:00
#SBATCH --mem-per-cpu=16G
#SBATCH --array=1-1000

perm=$SLURM_ARRAY_TASK_ID

train_vectors='data/word2vec_vectors_final.mat'

sub="average"
ch_type="grad"
position='target'
level=$1
test_level=$2
train_time=$3

python 03_decoding/zero_shot_run.py 'data/matrices/'$sub'_position-'$position'_level-'$level'_channels-'$ch_type'.mat' \
-input_file2 'data/matrices/'$sub'_position-'$position'_level-'$test_level'_channels-'$ch_type'.mat' \
-o 'results/tc_'$level'/perm/'$sub'_position-'$position'_train_level-'$level'_test_level-'$test_level'_channels-'$ch_type'-'$train_time'_tc_perm-'$perm'.mat' -n $vectors -v -tc 5 -t $train_time -p $perm


python 03_decoding/zero_shot_analyze_results.py 'results/tc_'$level'/perm/'$sub'_position-'$position'_train_level-'$level'_test_level-'$test_level'_channels-'$ch_type'-'$train_time'_tc_perm-'$perm'.mat' \
-o 'results/tc_'$level'/perm/'$sub'_position-'$position'_train_level-'$level'_test_level-'$test_level'_channels-'$ch_type'-'$train_time'_tc_perm-'$perm'.csv'






