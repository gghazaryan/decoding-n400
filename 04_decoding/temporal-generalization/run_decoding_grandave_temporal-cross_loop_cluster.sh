#!/bin/bash

# Define the levels to loop through
levels=("combined" "level1" "level2" "level3")
#levels=("combined")

# Define the test levels
test_levels=("level1" "level2" "level3")

# Loop through each level
for level in "${levels[@]}"; do
for test_level in "${test_levels[@]}"; do

sbatch run_decoding_grandave_temporal-cross_triton.sh "$level" "$test_level"

done
done
