#!/bin/bash

# Define the levels to loop through
levels=("level1" "level2" "level3")
ch_groups=("grad")
windows=(0 1 2)

# Loop through each level
for channels in "${ch_groups[@]}"; do
for level in "${levels[@]}"; do
for window in "${windows[@]}"; do

04_decoding/sensor-level-windows/run_decoding_grandave_windows_local.sh "$level" "$channels" "$window"

done
done
done
