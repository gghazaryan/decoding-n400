#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evoked responses.

@author: Gayane Ghazaryan
"""

import sys

sys.path.append("..")
import argparse
import mne
from config import fname, filter_list
from pathlib import Path
import pandas as pd


# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--subject", type=int, metavar="sub###", help="The subject to process"
)
args = parser.parse_args()

# Check if the required arguments are provided
if not (args.subject):
    subject = int(input("Enter the value for subject: "))
else:
    subject = args.subject


print("Processing subject:", subject)


df_all = pd.read_csv(fname.all_trials_file)[["Word", "Category"]]
df_all.columns = ["target", "category"]

targets = df_all["target"]

# short evokeds
positions = ["prime1", "prime2", "target"]

for f in filter_list:
    highpass, lowpass = f

    all_epochs_short = {}
    for position in positions:
        all_epochs_short[position] = mne.read_epochs(
            fname.clean_epo_merged_dropbad(
                subject=subject, position=position, highpass=highpass, lowpass=lowpass
            )
        )

    # averaged by position, e.g. target prime1 prime2
    evokeds_short = []
    for position in positions:
        evokeds_short.append(
            all_epochs_short[position]
            .copy()
            .average()
            .apply_baseline((-0.1, 0))
            .crop(0, 1)
        )

    Path(
        fname.ave_positions(subject=subject, highpass=highpass, lowpass=lowpass)
    ).parent.mkdir(parents=True, exist_ok=True)

    mne.write_evokeds(
        fname.ave_positions(subject=subject, highpass=highpass, lowpass=lowpass),
        evokeds_short,
        overwrite=True,
    )

    # averaged by level, all words together within position
    for position in positions:
        all_epochs_target = all_epochs_short[position]

        ave_list_short = []
        for idx_level, level in enumerate(["level1", "level2", "level3"]):
            ave = all_epochs_target[level].apply_baseline((-0.1, 0)).average()
            ave_list_short.append(ave)

        mne.write_evokeds(
            fname.ave_levels(
                subject=subject, highpass=highpass, lowpass=lowpass, position=position
            ),
            ave_list_short,
            overwrite=True,
        )

    # word by word
    for position in positions:
        for level in ["level1", "level2", "level3", "all"]:
            current_level_evokeds = []
            level_epochs = all_epochs_short[position]
            level_epochs.apply_baseline((-0.1, 0))
            for current_word in targets:
                current_epochs = level_epochs[current_word]
                if level == "all":
                    current_evoked = current_epochs.average()
                else:
                    current_evoked = current_epochs[level].average()
                current_level_evokeds.append(current_evoked)
            mne.write_evokeds(
                fname.ave_indiv(
                    subject=subject,
                    highpass=highpass,
                    lowpass=lowpass,
                    position=position,
                    level=level,
                ),
                current_level_evokeds,
                overwrite=True,
            )

    # long evokeds
    # =============================================================================
    #     all_epochs_long = mne.read_epochs(fname.clean_epo_merged_long(subject = subject, position="prime1",highpass=highpass,lowpass=lowpass))
    #
    #     evokeds_long=all_epochs_long.average().apply_baseline((-0.1,0)).crop(-0.1,3)
    #
    #     mne.write_evokeds(fname.ave_long(subject=subject,highpass=highpass,lowpass=lowpass),evokeds_long,overwrite=True)
    #
    #
    #     ave_list_long = []
    #     for idx_level, level in enumerate(['level1','level2','level3']):
    #         ave = all_epochs_long[level].apply_baseline((-0.1,0)).average()
    #         ave_list_long.append(ave)
    #
    #
    #     mne.write_evokeds(fname.ave_long_levels(subject=subject,highpass=highpass,lowpass=lowpass),ave_list_long,overwrite=True)
    # =============================================================================

    # long item level evokeds
    # =============================================================================
    #     for level in ["level1","level2","level3","all"]:
    #         current_level_evokeds = []
    #         for current_word in targets:
    #             current_epochs = all_epochs_long['prime1'][current_word]
    #             if level == "all":
    #                 current_evoked = current_epochs.apply_baseline((-0.1,0)).average()
    #             else:
    #                 current_evoked = current_epochs[level].apply_baseline((-0.1,0)).average()
    #             current_level_evokeds.append(current_evoked)
    #         mne.write_evokeds(fname.ave_long_indiv(subject=subject,highpass=highpass,lowpass=lowpass,position='prime1',level=level),current_level_evokeds,overwrite=True)
    # =============================================================================

    del all_epochs_short, evokeds_short  # all_epochs_long, ave_list_long
