#!/bin/bash

# Define the levels to loop through
levels=("level1" "level2" "level3")
ch_groups=("grad")


# Loop through each level
for channels in "${ch_groups[@]}"; do
for level in "${levels[@]}"; do


sbatch 04_decoding/sensor-level-windows/run_decoding_grandave_windows_cluster.sh "$level" "$channels" 

done
done

