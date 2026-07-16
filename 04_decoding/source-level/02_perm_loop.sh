#!/usr/bin/env bash

levels=("level1" "level2" "level3")
train_level="combined"
windows=("100 300" "300 500" "500 700")


for test_level in "${levels[@]}"; do
  for w in "${windows[@]}"; do
    read -r tmin tmax <<< "$w"  
	sbatch 02_perm_combined.sh "$train_level" "$test_level" "$tmin" "$tmax" 
     
    done
  done


