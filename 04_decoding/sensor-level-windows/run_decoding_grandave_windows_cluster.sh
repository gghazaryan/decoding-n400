#!/bin/bash 
#SBATCH --time=00:30:00
#SBATCH --mem-per-cpu=2G
#SBATCH --array=0-2

window=$SLURM_ARRAY_TASK_ID
train_vectors='data/word2vec_vectors_final.mat'


sub="average"
highpass=0.1
lowpass=40
position='target'
folder='highpass-'$highpass'_lowpass-'$lowpass''
level='combined' #train_level change to $1 for within level training
test_level=$1
ch_type=$2


python 03_decoding/zero_shot_run.py 'data/matrices/'$sub'_position-'$position'_level-'$level'_'$window'_channels-'$ch_type'.mat' -input_file2 'data/matrices/'$sub'_position-'$position'_level-'$test_level'_'$window'_channels-'$ch_type'.mat' -o 'results/decoding_windows/'$sub'_position-'$position'_train_level-'$level'_test_level-'$test_level'_channels-'$ch_type'-'$window'_window.mat' -n $train_vectors -v

python 03_decoding/zero_shot_analyze_results.py 'results/decoding_windows/'$sub'_position-'$position'_train_level-'$level'_test_level-'$test_level'_channels-'$ch_type'-'$window'_window.mat' -o 'results/decoding_windows/'$sub'_position-'$position'_train_level-'$level'_test_level-'$test_level'_channels-'$ch_type'-'$window'_window.csv'
