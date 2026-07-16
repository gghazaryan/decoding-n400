# When meaning becomes decodable

Analysis code for When meaning becomes decodable: Linking the N400 evoked response to semantic representations (2026). Gayane Ghazaryan, Aino Saranpää, Tiina Lindh-Knuutila, Marijn van Vliet, Riitta Salmelin.

## Scripts

- `01_preprocessing/`: scripts to perform preprocessing on the subject-level MEG data
- `02_source_localize/`: scripts to source-localize the MEG signal
- `03_evokeds_analysis/`: scripts for the comparison of evoked responses
- `04_decoding/`: scripts for the zero-shot decoding analysis (separate windows, temporal generalization and source-level)
- `05_stimuli/`: scripts for comparison of stimuli

## How to use

Due to data sharing limitations, individual participant data cannot be shared. Only the grand average data is shared.
From this, all figures can be generated using the following scripts:

- `02_source_localize/05_3_source_comp_plot.py`: plots the grand average cortical-level comparisons between levels.
- `03_evokeds_analysis/evokeds_plot.R`: calculates and plots the evoked responses.
- `04_decoding/sensor-level/windows_overall.R`: calculates the significance of and plots the zero-shot decoding accuracy for the three windows.
- `04_decoding/temporal-generalization/temporal_cross.R`: calculates the significance of and plots the temporal generalization maps.
- `04_decoding/source-level/source_level_vis_sig.py`: plots the cortical-level searchlight decoding results.
- `05_stimuli/stimuli_stats.R`: calculates and plots statistics of the stimuli.

To regenerate the results and figures:

- install required system dependencies for R packages (e.g. on Ubuntu):
```bash
sudo apt install -y \
  cmake \
  gdal-bin \
  gsfonts \
  libabsl-dev \
  libcurl4-openssl-dev \
  libfontconfig1-dev \
  libfreetype6-dev \
  libgdal-dev \
  libglpk-dev \
  libicu-dev \
  libmagick++-dev \
  libpng-dev \
  libssl-dev \
  libudunits2-dev \
  libx11-dev \
  libxml2-dev \
  make \
  pandoc

```
- install the required dependencies (for Python 3.10.11 and R 4.3.3)
```bash
uv sync
Rscript -e 'renv::restore(prompt = FALSE)'
```
- download the provided data from 
- run the scripts in order or run `uv run --frozen bash generate_figures.sh`

To run the zero-shot-decoding analysis locally for the time windows use:

```bash
uv run bash ./04_decoding/sensor-level-windows/run_decoding_grandave_windows_loop_local.sh
```

Cross-temporal and source-level decoding analysis scripts are for HPC use.
