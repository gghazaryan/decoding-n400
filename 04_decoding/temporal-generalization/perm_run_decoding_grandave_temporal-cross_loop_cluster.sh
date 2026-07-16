#!/bin/bash

# Define the levels to loop through
levels=("level1" "level2" "level3" "combined")
levels=("combined")
# Define the test levels
test_levels=("level1" "level2" "level3")


# Loop through each level

for train_time in {0..45}; do
for level in "${levels[@]}"; do
for test_level in "${test_levels[@]}"; do

sbatch perm_run_decoding_grandave_temporal-cross_triton.sh $level $test_level $train_time

done
done
done
