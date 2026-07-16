#!/bin/bash

export QT_QPA_PLATFORM=xcb

mkdir -p figures
#python 02_source_localize/00_source_space_setup.py
#python 02_source_localize/05_3_source_comp_plot.py
Rscript 03_evokeds_analysis/evokeds_plot.R
Rscript 04_decoding/sensor-level-windows/windows_overall.R
Rscript 04_decoding/temporal-generalization/temporal_cross.R
#python 04_decoding/source-level/08_source_level_vis_sig.py
Rscript 05_stimuli/stimuli_stats.R
