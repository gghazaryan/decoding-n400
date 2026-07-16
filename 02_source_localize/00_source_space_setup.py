#!/usr/bin/env python3

import mne

subjects_dir = "data/"
output_file = "data/fsaverage/fsaverage-ico4-src.fif"

mne.datasets.fetch_fsaverage(subjects_dir=subjects_dir)

src = mne.setup_source_space(
    subject="fsaverage",
    spacing="ico4",
    subjects_dir=subjects_dir,
    add_dist=True,
)

mne.write_source_spaces(output_file, src, overwrite=True)
