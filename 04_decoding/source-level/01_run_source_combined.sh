#!/bin/bash 
#SBATCH --time=04:00:00
#SBATCH --mem=1G
#SBATCH -n 1
#SBATCH --array=0-122

patch_file="patches.tsv"

TOTAL=5124
PER_TASK=42


start=$((SLURM_ARRAY_TASK_ID * PER_TASK))
end=$((start + PER_TASK - 1))
if (( end >= TOTAL )); then end=$((TOTAL-1)); fi

for ((j=start; j<=end; j++)); do
  echo "Task $SLURM_ARRAY_TASK_ID running job $j"
  
patch=$j
train_level=$1
test_level=$2
tmin=$3
tmax=$4

in_path="data/source-level/group_average/decoding_mats"
out_path="results/decoding/source-level"

train_file="${in_path}/average-${train_level}_${tmin}-${tmax}.mat"
test_file="${in_path}/average-${test_level}_${tmin}-${tmax}.mat"
decoding_mat="${out_path}/${train_level}-${test_level}/${tmin}-${tmax}/patch${patch}-${test_level}.mat"
decoding_csv="${out_path}/${train_level}-${test_level}/${tmin}-${tmax}/patch${patch}-${test_level}.csv"

verts="$(03_decoding/source-level/00_get_patch_vertices.sh "$patch_file" "$patch")"  
python 03_decoding/zero_shot_run.py $train_file -input_file2 $test_file -verts $verts -n 'data/vectors/word2vec_vectors_final.mat' -v -o $decoding_mat 
python 03_decoding/zero_shot_analyze_results.py $decoding_mat -o $decoding_csv

rm $decoding_mat
done
