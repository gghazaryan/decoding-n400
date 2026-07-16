#!/bin/bash 
#SBATCH --time=00:10:00
#SBATCH --mem=2G
#SBATCH -n 1

merged_file=$2
in_dir=$1
: > $merged_file
first=1


for f in $(ls -1 ${in_dir}/*.csv | sort -V); do
  if (( first )); then
    cat $f >> $merged_file
    first=0
  else
    tail -n +2 $f >> $merged_file
  fi
done
rm -r $in_dir
