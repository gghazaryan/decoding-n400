#!/usr/bin/env bash
# Prints the vertex indices (2nd column) for patch index 7 (1st column)

awk -F'\t' -v idx="$2" 'NR>1 && $1==idx {print $2; exit}' "$1"

