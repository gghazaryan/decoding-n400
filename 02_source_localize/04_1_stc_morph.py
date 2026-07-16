#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Morph STCs.

@author: Gayane Ghazaryan
"""

import sys

sys.path.append("..")
import mne
from config import fname
import argparse
import os
from pathlib import Path
import numpy as np
import pandas as pd


# Be verbose
mne.set_log_level("INFO")

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--subject", type=int, metavar="sub###", help="The subject to process"
)
args = parser.parse_args()
subject = args.subject
print("Processing subject:", subject)


if not (args.subject):
    subject = int(input("Enter the value for subject (1,2,3): "))

else:
    subject = args.subject

src_to = mne.read_source_spaces(fname.src_fsaverage)

inverse_operator = mne.minimum_norm.read_inverse_operator(fname.inv(subject=subject))
morph = mne.compute_source_morph(
    inverse_operator["src"],
    subject_from=f"sub-{subject:02d}",
    subject_to="fsaverage",
    src_to=src_to,
    subjects_dir=fname.freesurfer_subjects_dir,
)

# =============================================================================
# # Create the source space for fsaverage
# fsaverage_src = mne.setup_source_space('fsaverage', spacing='ico4', add_dist=False,
#                                              subjects_dir=fname.freesurfer_subjects_dir)
#
# # Save the source space for later use2
# fsaverage_src.save(fname.src_fsaverage, overwrite=True)
# =============================================================================

# morphing


for level in ["level1", "level2", "level3", "all"]:
    all_items_stc = mne.read_source_estimate(
        fname.all_items_stc(subject=subject, level=level)
    )
    all_items_stc_fsaverage = morph.apply(all_items_stc)
    all_items_stc_fsaverage.save(
        fname.all_items_stc_morphed(subject=subject, level=level), overwrite=True
    )


# morphing individual


df_all = pd.read_csv(fname.all_trials_file)[["Word", "Category"]]
df_all.columns = ["target", "category"]
targets = df_all["target"]

for level in ["level1", "level2", "level3", "all"]:
    print(level)
    for item in targets:
        stc_f = fname.indiv_item_stc(item=item, subject=subject, level=level)
        item_stc = mne.read_source_estimate(stc_f)
        item_stc_fsaverage = morph.apply(item_stc)
        item_stc_fsaverage.save(
            fname.indiv_item_stc_morphed(subject=subject, level=level, item=item),
            overwrite=True,
        )
