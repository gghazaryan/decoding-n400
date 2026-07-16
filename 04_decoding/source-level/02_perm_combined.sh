#!/bin/bash 
#SBATCH --time=96:00:00
#SBATCH --mem=1G
#SBATCH -n 1
#SBATCH --job-name=perm
#SBATCH --array=1-1000

patch_file="patches.tsv"


patch=$SLURM_ARRAY_TASK_ID
train_level=$1
test_level=$2
tmin=$3
tmax=$4

tmp_base="/tmp"

in_path="data/source-level/group_average/decoding_mats"
out_path="results/source-level/perm"
merge_dir="${out_path}/${train_level}-${test_level}/${tmin}-${tmax}"

mkdir -p $merge_dir

merged_csv="${merge_dir}/patch${patch}_${train_level}-${test_level}_${tmin}-${tmax}_merged.csv"

exec 9> "$merged_csv"

verts="$(./00_get_patch_vertices.sh "$patch_file" "$patch")"

for perm in $(seq 1 1000); do

train_file="${in_path}/average-${train_level}_${tmin}-${tmax}.mat"
test_file="${in_path}/average-${test_level}_${tmin}-${tmax}.mat"

decoding_mat="${tmp_base}/${train_level}-${test_level}/${patch}-${perm}.mat"
decoding_csv="${tmp_base}/${train_level}-${test_level}/${patch}-${perm}.csv"


python 03_decoding/zero_shot_run.py $train_file -input_file2 $test_file -verts $verts -n 'data/word2vec_vectors_final.mat' -v -o $decoding_mat -p $perm
python 03_decoding/zero_shot_analyze_results.py $decoding_mat -o $decoding_csv

rm -f $decoding_mat $decoding_csv

done
