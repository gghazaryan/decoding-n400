#!/bin/bash 
#SBATCH --time=04:00:00
#SBATCH --mem-per-cpu=16G
#SBATCH --array=0-1000

train_time=$SLURM_ARRAY_TASK_ID

train_vectors='data/vectors/word2vec_vectors_final.mat'

sub="average"
ch_type="grad"
position='target'
level=$1 #train_level
test_level=$2

python 03_decoding/zero_shot_run.py 'data/matrices/'$sub'_position-'$position'_level-'$level'_channels-'$ch_type'.mat' \
-input_file2 'data/matrices/'$sub'_position-'$position'_level-'$test_level'_channels-'$ch_type'.mat' \
-o 'results/tc_'$level'/'$sub'_position-'$position'_train_level-'$level'_test_level-'$test_level'_channels-'$ch_type'-'$train_time'_tc.mat' -n $train_vectors -v -tc 5 -t $train_time

python 03_decoding/zero_shot_analyze_results.py 'results/tc_'$level'/'$sub'_position-'$position'_train_level-'$level'_test_level-'$test_level'_channels-'$ch_type'-'$train_time'_tc.mat' \
-o 'results/tc_'$level'/'$sub'_position-'$position'_train_level-'$level'_test_level-'$test_level'_channels-'$ch_type'-'$train_time'_tc.csv'
