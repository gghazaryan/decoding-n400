#!/usr/bin/env bash

levels=("level1" "level2" "level3")
windows=("100 300" "300 500" "500 700")
train_level="combined"

for test_level in "${levels[@]}"; do
  prev_merge=""
  for w in "${windows[@]}"; do
    read -r tmin tmax <<< "$w"

    if [[ -n "$prev_merge" ]]; then
      id_main=$(sbatch --parsable --dependency=afterok:"$prev_merge" \
        01_run_source_combined.sh $train_level $test_level $tmin $tmax)
    else
      id_main=$(sbatch --parsable \
        01_run_source_combined.sh $train_level $test_level $tmin $tmax)
    fi
    csv_dir="results/source-level/${train_level}-${test_level}/${tmin}-${tmax}"
    merged_csv="results/source-level/${train_level}-${test_level}_${tmin}-${tmax}_merged.csv"

    prev_merge=$(sbatch --parsable --dependency=afterok:"$id_main" \
      03_csv_join.sh $csv_dir $merged_csv)
  done
done

