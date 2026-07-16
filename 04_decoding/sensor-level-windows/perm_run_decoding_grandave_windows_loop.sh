#!/bin/bash

# Define the levels to loop through
levels=("level1" "level2" "level3")
windows=(0 1 2)

# Loop through each level
for window in "${windows[@]}"; do
for level in "${levels[@]}"; do

sbatch perm_run_decoding_grandave_windows.sh "$level" "$window"

done
done
