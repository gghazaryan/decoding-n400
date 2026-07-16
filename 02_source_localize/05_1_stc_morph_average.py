#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STC morph average.

@author: Gayane Ghazaryan
"""

import sys

sys.path.append("../")
import mne
from config import fname
import argparse
from pathlib import Path
import numpy as np
import pandas as pd


# Be verbose
mne.set_log_level("INFO")
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--nsubject", type=int, metavar="sub###", help="The number of participants"
)
parser.add_argument(
    "--exclude", nargs="+", help="A list of subjects to be excluded", required=True
)
args = parser.parse_args()
n = args.nsubject
exclude = args.exclude
print("Number of total participnats:", n)

exclude = list(set([int(i) for i in exclude]))
print("Excluding subjects:", exclude)


for level in ["level1", "level2", "level3", "all"]:
    all_subject_stcs = []
    for subject in range(1, n + 1):
        if subject not in exclude:
            all_items_stc_morphed = mne.read_source_estimate(
                fname.all_items_stc_morphed(subject=subject, level=level)
            )
            all_subject_stcs.append(all_items_stc_morphed)

    average_stc = np.mean(all_subject_stcs)
    Path(fname.average_stc(level=level)).parent.mkdir(parents=True, exist_ok=True)
    average_stc.save(fname.average_stc(level=level), overwrite=True)


# morphing individual items
all_trials_file = fname.all_trials_file

df_all = pd.read_csv(all_trials_file)[["Word", "Category"]]
df_all.columns = ["target", "category"]
targets = df_all["target"]

for level in ["level1", "level2", "level3", "all"]:
    print(level)
    for item in targets:
        all_subject_stcs = []
        for subject in range(1, n + 1):
            if subject not in exclude:
                item_stc_morphed = mne.read_source_estimate(
                    fname.indiv_item_stc_morphed(
                        subject=subject, level=level, item=item
                    )
                )
                all_subject_stcs.append(item_stc_morphed)
        item_average_stc = np.mean(all_subject_stcs)
        Path(fname.item_average_stc(level=level, item=item)).parent.mkdir(
            parents=True, exist_ok=True
        )
        item_average_stc.save(
            fname.item_average_stc(level=level, item=item), overwrite=True
        )
